# Milestone 1 API contract

API prefix `/api`. Development UI forwards `/api` to `http://127.0.0.1:8000`. No CORS wildcard, remote exposure or authentication required for this loopback-only prototype.

`GET /api/health` returns `{ "status": "ok", "mode": "synthetic_demo", "orders_enabled": false }`.

`GET /api/demo` returns:
```json
{
  "mode": "synthetic_demo",
  "label": "Synthetic demo data — not current market data",
  "source": "Bundled synthetic fixtures",
  "replay_times": ["2026-10-30T09:30:00+05:30", "2026-10-30T09:35:00+05:30", "2026-10-30T09:40:00+05:30"],
  "default_as_of": "2026-10-30T09:35:00+05:30"
}
```

`GET /api/replay?as_of=<URL encoded ISO8601 with offset>` returns this shape. All optional values are JSON null, not NaN. `rank` ranks only qualified screens, sorted by relative return descending with symbol as tie breaker. Other cards have null rank. ALL five fixture underlyings have cards, including exclusions.
```json
{
  "mode": "synthetic_demo",
  "as_of": "2026-10-30T09:35:00+05:30",
  "rule_version": "opening-range-v0.1",
  "source": "Bundled synthetic fixtures",
  "summary": {"total": 5, "qualified": 1, "watching": 1, "blocked": 3},
  "candidates": [{
    "symbol": "DEMO_ALPHA", "name": "Alpha Industries (fictional)", "sector": "Industrials",
    "rank": 1, "state": "qualified", "reason_codes": ["BREAKOUT_CONFIRMED"],
    "reasons": ["A completed close is above the first 15-minute range and relative return is positive."],
    "last_price": 103.0, "last_bar_end": "2026-10-30T09:35:00+05:30",
    "opening_range_high": 102.0, "opening_range_low": 99.0,
    "return_pct": 3.0, "benchmark_return_pct": 0.3, "relative_return_pct": 2.7,
    "eligibility": "eligible", "fundamentals_status": "available",
    "evidence": [{"id": "alpha-results-v1", "kind": "quarterly_result", "title": "Synthetic quarterly result",
      "summary": "Illustrative revenue growth, not a real company filing.", "period": "DEMO quarter",
      "source": "Synthetic fixture", "source_url": null,
      "published_at": "2026-10-30T08:30:00+05:30", "available_at": "2026-10-30T08:31:00+05:30"}],
    "bars": [{"bar_end":"2026-10-30T09:20:00+05:30","close":100.0}],
    "contract_status": "not_evaluated"
  }]
}
```

Allowed `state`: `qualified`, `watching`, `blocked`. Allowed `eligibility`: `eligible`, `ineligible`, `unknown`. `fundamentals_status`: `available`, `unknown`. API rejects naive/malformed timestamps with HTTP 422. Report invalid local datasets on startup with file/row errors. No HTTP upload route in this milestone. Backend CSV loader can read a custom directory through an explicit CLI validation command; default HTTP server always serves bundled synthetic fixtures to avoid mislabelling imported real data.

The prototype returns screens, not trade instructions. All contract statuses stay `not_evaluated`. No buy/sell buttons, option prices, lot sizes or returns are manufactured.

## Milestone 2A: `GET /api/data-coverage`

This independent read-only route never changes `/api/demo`, `/api/replay`, synthetic labels, qualification or `contract_status: not_evaluated`. It reads only the operator-configured `TRADE_COVERAGE_REPORT` path; query parameters cannot select another path. No upload, document/raw-data serving, source-URL fetch or filesystem browsing endpoints exist.

The response envelope has `api_version: "coverage-api-v1"`:

```json
{"api_version":"coverage-api-v1","state":"not_imported","report":null}
```

- `not_imported`: environment variable unset/empty.
- `invalid_report`: configured file missing/unreadable, incompatible version, malformed/nonfinite content or contradictory coverage fields. `report` is null and filesystem errors/paths are not returned.
- `report`: `report` contains the validated projection below. `report.status` distinguishes `partial`, `invalid` (input material), and `coverage_complete`.

These domain states use HTTP 200. Transport/server failures remain HTTP/network errors and are shown separately by the client, with no substituted coverage. A refresh clears the prior result while fetching. Incompatible API/report versions are rejected by both backend and frontend.

The configured file is a local `intake-run-v1` JSON envelope, whose `coverage` field conforms to `coverage-v1`. Its `provenance` and `diagnostics` are private and never returned. The API's report fields are:

| Field | Contract |
| --- | --- |
| `schema_version`, `parser_version` | `coverage-v1`, `local-intake-v1`. |
| `status`, `schema_valid` | `partial`/`invalid`/`coverage_complete`; schema validity is separate from gaps and is false for invalid inputs. |
| `dataset_id`, `dataset_nature`, `source_label` | Short safe label or null; nature is `synthetic_test`/`user_import`/null. A complete synthetic report is explicitly not a real-data trial. |
| `session_date`, `imported_at` | ISO session date or null; actual offset-bearing ingestion timestamp. No historical observed availability is claimed. |
| `stock_count`, `benchmark` | Three equities and `NIFTY50` for a declared sample; zero/null when the manifest is unavailable/invalid. |
| `series` | Array of four selected instruments, or empty before a valid manifest. |
| `series[]` | `symbol`, `instrument_type` (`equity`/`spot_index`), `expected` (9), `present`, `missing` (interval-start HH:MM strings), `duplicates`, `outside_window`, `missing_volume`. Unique counts and missing intervals must agree. |
| `membership[]` | Three equities: `symbol`, `level` (`unknown`/`user_assertion`/`supporting_evidence`), `dated_review` (explicit manual confirmation supported by a matching document and effective date). Not independently verified exchange eligibility. |
| `universe_count`, `list_duplicates`, `unmapped_symbols` | Full list counts. Extra universe symbols do not expand the 36-bar sample. |
| `invalid_rows`, `outside_window`, `duplicate_rows` | Separate candle validation counters. Missing spot-index volume does not erase a bar. |
| `source_review`, `session_review` | `pending` or `manual_confirmed`; distinct from structural validity. |
| `price_adjustment`, `source_dates_known`, `retention` | `adjusted`/`unadjusted`/`unknown`; boolean known source/as-of date; `permitted`/`unresolved`. |
| `filing` | `status` (`not_imported`/`imported`), `symbol` or null, `publication_precision` (`exact`/`date_only`/`unknown`), `reconciliation` (`unreviewed`/`transcribed`/`reconciled`), `figures_present` (0–3), `source_known` (boolean). No financial values are exposed by this coverage route. |
| `gaps` | Stable codes translated into actionable text by the UI; see `frontend/src/coverage.ts` and the completion rules in `docs/MILESTONE_2A.md`. |

A complete sanitized synthetic response is retained as a software test fixture in `frontend/tests/coverageFixture.json`. Counts must be finite non-negative integers. Report fields do not contain local paths, source URLs, document/row references, raw data, file hashes, account records or secrets. Unknown/extra fields in the report model are rejected. The file itself is local operator input, not an independently authenticated data source.
