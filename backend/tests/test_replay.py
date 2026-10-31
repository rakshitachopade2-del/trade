import csv
import json
import shutil
import tempfile
import unittest
from dataclasses import replace
from datetime import timedelta
from pathlib import Path

from backend.app.engine import replay
from backend.app.loader import DEMO_DIRECTORY, DataValidationError, load_dataset, parse_timestamp


def at(clock):
    return parse_timestamp(f"2026-10-30T{clock}:00+05:30")


def card(result, symbol="DEMO_ALPHA"):
    return next(item for item in result["candidates"] if item["symbol"] == symbol)


class ReplayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = load_dataset()

    def test_fixture_states_and_time_gated_evidence(self):
        opening = replay(self.data, at("09:30"))
        self.assertEqual(opening["summary"]["qualified"], 0)
        self.assertEqual(card(opening)["state"], "watching")
        result = replay(self.data, at("09:35"))
        self.assertEqual(result["summary"], {"total": 5, "qualified": 1, "watching": 1, "blocked": 3})
        alpha = card(result)
        self.assertEqual((alpha["state"], alpha["rank"]), ("qualified", 1))
        self.assertEqual((alpha["opening_range_high"], alpha["opening_range_low"]), (102, 99))
        self.assertEqual((alpha["return_pct"], alpha["benchmark_return_pct"], alpha["relative_return_pct"]), (3, .3, 2.7))
        self.assertEqual(card(result, "DEMO_BETA")["fundamentals_status"], "unknown")
        later = card(replay(self.data, at("09:40")), "DEMO_BETA")
        self.assertEqual(later["fundamentals_status"], "available")
        self.assertEqual([item["id"] for item in later["evidence"]], ["beta-results-v1"])

    def test_unknown_and_ineligible_are_never_ranked(self):
        result = replay(self.data, at("09:35"))
        for symbol, eligibility in (("DEMO_GAMMA", "ineligible"), ("DEMO_DELTA", "unknown")):
            item = card(result, symbol)
            self.assertEqual(item["state"], "blocked")
            self.assertEqual(item["eligibility"], eligibility)
            self.assertIsNone(item["rank"])

    def test_no_lookahead_when_future_data_changes(self):
        expected = replay(self.data, at("09:35"))
        future_bars = tuple(replace(bar, open=999999, high=1000000, low=999998, close=999999)
                            if bar.bar_end > at("09:35") else bar for bar in self.data.bars)
        future_evidence = tuple(replace(item, title="Future secret", summary="A future fact")
                                if item.available_at > at("09:35") else item for item in self.data.evidence)
        future_eligibility = replace(self.data.eligibility[0], status="ineligible", available_at=at("09:40"))
        changed = replace(self.data, bars=future_bars, evidence=future_evidence,
                          eligibility=self.data.eligibility + (future_eligibility,))
        self.assertEqual(replay(changed, at("09:35")), expected)

    def test_ended_but_not_available_candle_is_excluded(self):
        changed = replace(self.data, bars=tuple(replace(bar, available_at=at("09:36"))
                          if bar.symbol == "DEMO_ALPHA" and bar.bar_end == at("09:35") else bar
                          for bar in self.data.bars))
        item = card(replay(changed, at("09:35")))
        self.assertEqual(item["last_bar_end"], at("09:30").isoformat())
        self.assertEqual(item["state"], "watching")

    def test_available_but_unfinished_candle_is_excluded(self):
        changed = replace(self.data, bars=tuple(replace(bar, available_at=at("09:36"))
                          if bar.bar_end == at("09:40") else bar for bar in self.data.bars))
        result = replay(changed, at("09:37"))
        self.assertTrue(all(parse_timestamp(bar["bar_end"]) <= at("09:37")
                            for item in result["candidates"] for bar in item["bars"]))
        self.assertEqual(card(result)["last_price"], 103)

    def test_missing_opening_bar_does_not_shrink_range(self):
        changed = replace(self.data, bars=tuple(bar for bar in self.data.bars
                          if not (bar.symbol == "DEMO_ALPHA" and bar.bar_end == at("09:25"))))
        item = card(replay(changed, at("09:35")))
        self.assertEqual(item["state"], "blocked")
        self.assertIn("INCOMPLETE_OPENING_RANGE", item["reason_codes"])
        self.assertIn("MISSING_BARS", item["reason_codes"])
        self.assertIsNone(item["opening_range_high"])

    def test_missing_post_range_bar_blocks_later_trigger(self):
        changed = replace(self.data, bars=tuple(bar for bar in self.data.bars
                          if not (bar.symbol == "DEMO_ALPHA" and bar.bar_end == at("09:35"))))
        item = card(replay(changed, at("09:40")))
        self.assertEqual(item["state"], "blocked")
        self.assertIn("MISSING_BARS", item["reason_codes"])

    def test_freshness_boundary_and_outside_sample_session(self):
        self.assertNotIn("STALE_DATA", card(replay(self.data, at("09:45")))["reason_codes"])
        result = replay(self.data, parse_timestamp("2026-10-30T09:45:01+05:30"))
        self.assertIn("STALE_DATA", card(result)["reason_codes"])
        after_session = replay(self.data, at("16:00"))
        self.assertEqual(after_session["summary"]["qualified"], 0)
        self.assertEqual(after_session["summary"]["blocked"], 5)

    def test_benchmark_missing_or_stale_never_becomes_zero(self):
        changed = replace(self.data, bars=tuple(bar for bar in self.data.bars
                          if not (bar.symbol == "DEMO_NIFTY" and bar.bar_end == at("09:35"))))
        item = card(replay(changed, at("09:35")))
        self.assertEqual(item["state"], "blocked")
        self.assertIn("BENCHMARK_UNAVAILABLE", item["reason_codes"])
        self.assertIsNone(item["benchmark_return_pct"])
        old = card(replay(self.data, at("09:46")))
        self.assertIn("BENCHMARK_STALE", old["reason_codes"])

    def test_eligibility_requires_publication_and_effective_interval(self):
        alpha = self.data.eligibility[0]
        for modified in (replace(alpha, available_at=at("09:40")),
                         replace(alpha, effective_from=at("09:40")),
                         replace(alpha, effective_to=at("09:35"))):
            with self.subTest(modified=modified):
                dataset = replace(self.data, eligibility=(modified,) + self.data.eligibility[1:])
                self.assertEqual(card(replay(dataset, at("09:35")))["eligibility"], "unknown")

    def test_later_known_eligibility_supersedes_previous(self):
        revised = replace(self.data.eligibility[0], status="ineligible", available_at=at("09:40"))
        dataset = replace(self.data, eligibility=self.data.eligibility + (revised,))
        self.assertEqual(card(replay(dataset, at("09:35")))["eligibility"], "eligible")
        self.assertEqual(card(replay(dataset, at("09:40")))["eligibility"], "ineligible")

    def test_news_does_not_imply_fundamentals_or_affect_rank(self):
        news = replace(self.data.evidence[0], kind="news")
        dataset = replace(self.data, evidence=(news,))
        result = card(replay(dataset, at("09:35")))
        self.assertEqual(result["fundamentals_status"], "unknown")
        self.assertEqual(result["rank"], 1)
        self.assertEqual(len(result["evidence"]), 1)

    def test_deterministic_ordering_and_tie_break(self):
        alpha_bars = tuple(replace(bar, symbol="DEMO_BETA") for bar in self.data.bars if bar.symbol == "DEMO_ALPHA")
        dataset = replace(self.data, bars=tuple(bar for bar in self.data.bars if bar.symbol != "DEMO_BETA") + alpha_bars)
        expected = replay(dataset, at("09:35"))
        shuffled = replace(dataset, bars=tuple(reversed(dataset.bars)), instruments=tuple(reversed(dataset.instruments)),
                           evidence=tuple(reversed(dataset.evidence)), eligibility=tuple(reversed(dataset.eligibility)))
        self.assertEqual(expected, replay(shuffled, at("09:35")))
        self.assertEqual([item["symbol"] for item in expected["candidates"] if item["rank"]],
                         ["DEMO_ALPHA", "DEMO_BETA"])
        json.dumps(expected, allow_nan=False)

    def test_utc_asof_is_equivalent_and_naive_rejected(self):
        self.assertEqual(replay(self.data, parse_timestamp("2026-10-30T04:05:00Z")),
                         replay(self.data, at("09:35")))
        with self.assertRaises(ValueError):
            replay(self.data, at("09:35").replace(tzinfo=None))

    def test_finite_inputs_cannot_emit_infinite_derived_returns(self):
        changed = replace(self.data, bars=tuple(replace(bar, open=1e-308, low=1e-308)
                          if bar.symbol == "DEMO_ALPHA" and bar.bar_start == at("09:15") else bar
                          for bar in self.data.bars))
        result = replay(changed, at("09:35"))
        item = card(result)
        self.assertEqual(item["state"], "blocked")
        self.assertIn("NUMERIC_OVERFLOW", item["reason_codes"])
        self.assertIsNone(item["return_pct"])
        json.dumps(result, allow_nan=False)


class CsvValidationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.directory = Path(self.temp.name)
        shutil.copytree(DEMO_DIRECTORY, self.directory, dirs_exist_ok=True)

    def tearDown(self):
        self.temp.cleanup()

    def edit(self, filename, mutate):
        path = self.directory / filename
        with path.open(newline="") as handle:
            reader = csv.DictReader(handle)
            fields, rows = reader.fieldnames, list(reader)
        mutate(rows)
        with path.open("w", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)

    def test_custom_directory_never_gets_demo_label(self):
        self.assertEqual(load_dataset(self.directory).mode, "unverified_import")

    def test_bad_ohlc_nan_infinity_zero_and_naive_times_fail_with_row(self):
        for field, value in (("high", "1"), ("open", "nan"), ("close", "inf"), ("low", "0"),
                             ("available_at", "2026-10-30T09:20:00")):
            with self.subTest(field=field, value=value):
                shutil.copy(DEMO_DIRECTORY / "prices.csv", self.directory / "prices.csv")
                self.edit("prices.csv", lambda rows: rows[0].update({field: value}))
                with self.assertRaisesRegex(DataValidationError, "prices.csv:row 2:"):
                    load_dataset(self.directory)

    def test_conflicting_duplicate_fails_identical_duplicate_deduplicates(self):
        self.edit("prices.csv", lambda rows: rows.append(dict(rows[0])))
        self.assertEqual(len(load_dataset(self.directory).bars), 27)
        self.edit("prices.csv", lambda rows: rows[-1].update({"close": "100.5"}))
        with self.assertRaisesRegex(DataValidationError, "conflicting duplicate"):
            load_dataset(self.directory)

    def test_evidence_time_order_and_ambiguous_eligibility_fail(self):
        self.edit("evidence.csv", lambda rows: rows[0].update({"available_at": "2026-10-30T08:00:00+05:30"}))
        with self.assertRaisesRegex(DataValidationError, "cannot precede published_at"):
            load_dataset(self.directory)
        shutil.copy(DEMO_DIRECTORY / "evidence.csv", self.directory / "evidence.csv")
        self.edit("eligibility.csv", lambda rows: rows.append({**rows[0], "status": "ineligible",
                                                              "effective_from": "2026-10-30T01:00:00+05:30"}))
        with self.assertRaisesRegex(DataValidationError, "contradictory overlapping"):
            load_dataset(self.directory)

    def test_csv_timestamps_normalize_to_ist(self):
        self.edit("prices.csv", lambda rows: rows[0].update({"bar_start": "2026-10-30T03:45:00Z",
                                                            "bar_end": "2026-10-30T03:50:00Z",
                                                            "available_at": "2026-10-30T03:50:00Z"}))
        self.assertEqual(load_dataset(self.directory).bars[0].bar_start, at("09:15"))

    def test_duplicate_headers_rejected_before_values_are_overwritten(self):
        path = self.directory / "prices.csv"
        text = path.read_text()
        path.write_text(text.replace("close,volume", "close,close", 1))
        with self.assertRaisesRegex(DataValidationError, "prices.csv:row 1: duplicate columns: close"):
            load_dataset(self.directory)

    def test_out_of_range_normalization_reports_file_and_row(self):
        for timestamp in ("0001-01-01T00:00:00+14:00", "9999-12-31T23:59:59-12:00"):
            with self.subTest(timestamp=timestamp):
                self.edit("prices.csv", lambda rows: rows[0].update({"available_at": timestamp}))
                with self.assertRaisesRegex(DataValidationError, "prices.csv:row 2:.*supported date range"):
                    load_dataset(self.directory)


if __name__ == "__main__":
    unittest.main()
