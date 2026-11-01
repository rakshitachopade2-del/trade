import copy
import csv
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timedelta
from unittest.mock import patch

from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.engine import replay
from backend.app.loader import load_dataset, parse_timestamp
from backend.app.intake.runner import run_import

ROOT = Path(__file__).resolve().parents[2]
OBSERVED = datetime.fromisoformat('2026-11-01T12:00:00+05:30')


class IntakeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / 'input'
        shutil.copytree(ROOT / 'data/intake-example', self.source)
        self.output = self.root / 'runs'

    def change(self, name, mutate):
        path = self.source / name
        value = json.loads(path.read_text())
        mutate(value)
        path.write_text(json.dumps(value))

    def rows(self):
        with (self.source / 'candles.csv').open() as handle:
            return list(csv.DictReader(handle))

    def write_rows(self, rows):
        with (self.source / 'candles.csv').open('w', newline='') as handle:
            writer = csv.DictWriter(handle, fieldnames=['symbol', 'timestamp', 'open', 'high', 'low', 'close', 'volume'])
            writer.writeheader(); writer.writerows(rows)

    def run_intake(self, **kwargs):
        directory, report = run_import(self.source, self.output, observed=kwargs.get('observed', OBSERVED))
        self.directory = directory
        self.envelope = json.loads((directory / 'report.json').read_text())
        return report

    def normalized(self):
        return json.loads((self.directory / 'normalized.json').read_text())

    def test_complete_sample_excludes_ten_oclock_start_and_retains_identity(self):
        result = self.run_intake()
        self.assertEqual(result.status, 'coverage_complete')
        self.assertEqual(result.dataset_nature, 'synthetic_test')
        self.assertEqual([s.present for s in result.series], [9, 9, 9, 9])
        self.assertEqual(result.stock_count, 3)
        self.assertEqual(result.outside_window, 1)
        self.assertEqual(sum(b['in_sample'] for b in self.normalized()['data']['bars']), 36)
        for name, digest in self.envelope['provenance']['files'].items():
            self.assertEqual(hashlib.sha256((self.directory / 'originals' / name).read_bytes()).hexdigest(), digest)

    def test_missing_equity_opening_and_benchmark_intervals_are_independent(self):
        self.write_rows([r for r in self.rows() if not (r['symbol'] in ['DEMO_ALPHA', 'DEMO_NIFTY'] and r['timestamp'].endswith('09:20:00+05:30'))])
        result = self.run_intake()
        self.assertEqual(result.status, 'partial')
        for series in result.series:
            self.assertEqual(series.present, 8 if series.symbol in ['DEMO_ALPHA', 'NIFTY50'] else 9)
            self.assertEqual(series.missing, ['09:20'] if series.present == 8 else [])
        self.assertEqual(sum(b['in_sample'] for b in self.normalized()['data']['bars']), 34)

    def test_duplicate_bars_identical_and_conflicting(self):
        rows = self.rows(); rows.append(copy.deepcopy(rows[0])); self.write_rows(rows)
        result = self.run_intake()
        self.assertEqual(result.duplicate_rows, 1)
        self.assertEqual(result.status, 'coverage_complete')
        rows[-1]['close'] = '100.5'; self.write_rows(rows)
        result = self.run_intake()
        self.assertEqual(result.status, 'invalid')
        self.assertEqual(result.series[0].present, 8)
        self.assertEqual(self.envelope['diagnostics'][0]['file'], 'candles.csv')
        self.assertEqual(self.envelope['diagnostics'][0]['row'], 39)

    def test_bad_ohlc_nonfinite_alignment_session_volume_and_column_count(self):
        original = self.rows()
        for field, value in [('open', 'NaN'), ('close', 'Infinity'), ('low', '999'), ('open', '0'),
                             ('timestamp', '2026-10-30T09:16:00+05:30'), ('timestamp', '2026-10-29T09:15:00+05:30'),
                             ('timestamp', '2026-10-30'), ('timestamp', '2026-10-30T09:15:00.0000001+05:30'),
                             ('volume', '-1'), ('volume', 'NaN')]:
            with self.subTest(field=field, value=value):
                rows = copy.deepcopy(original); rows[0][field] = value; self.write_rows(rows)
                result = self.run_intake()
                self.assertEqual(result.status, 'invalid')
                self.assertEqual(result.invalid_rows, 1)
                self.assertEqual(result.series[0].present, 8)
        (self.source / 'candles.csv').write_text('symbol,timestamp,open,high,low,close,volume\nDEMO_ALPHA,secret-unrelated-value\n')
        self.assertEqual(self.run_intake().status, 'invalid')
        self.assertNotIn('secret-unrelated-value', json.dumps(self.envelope))

    def test_duplicate_headers_and_ambiguous_or_unmapped_symbols(self):
        path = self.source / 'candles.csv'; original = path.read_text()
        path.write_text(original.replace('open,high', 'open,open'))
        self.assertEqual(self.run_intake().status, 'invalid')
        path.write_text(original)
        self.change('manifest.json', lambda m: m['instruments'][1].update(source_symbol=' demo_alpha '))
        self.assertEqual(self.run_intake().status, 'invalid')
        self.change('manifest.json', lambda m: m['instruments'][1].update(source_symbol='DEMO_BETA'))
        rows = self.rows(); rows[0]['symbol'] = 'Unknown Company'; self.write_rows(rows)
        report = self.run_intake()
        self.assertEqual(report.status, 'invalid')
        self.assertIn('mapping_unknown', report.gaps)

    def test_empty_review_references_and_source_symbols_are_invalid(self):
        self.change('manifest.json', lambda m: m['normal_session_review'].update(reference='   '))
        self.assertEqual(self.run_intake().status, 'invalid')
        self.change('manifest.json', lambda m: (m['normal_session_review'].update(reference='Synthetic fixture'), m['instruments'][0].update(source_symbol='   ')))
        self.assertEqual(self.run_intake().status, 'invalid')

    def test_start_end_offsets_and_naive_times_require_explicit_convention(self):
        self.run_intake(); baseline = self.normalized()['data']['bars']
        rows = self.rows()
        for row in rows:
            row['timestamp'] = (datetime.fromisoformat(row['timestamp']) + timedelta(minutes=5)).isoformat()
        self.write_rows(rows)
        self.change('manifest.json', lambda m: m.update(timestamp_convention='bar_end'))
        self.assertEqual(self.run_intake().status, 'coverage_complete')
        self.assertEqual([b['bar_start'] for b in self.normalized()['data']['bars']], [b['bar_start'] for b in baseline])
        for row in rows:
            row['timestamp'] = row['timestamp'].replace('+05:30', '')
        self.write_rows(rows)
        self.assertEqual(self.run_intake().status, 'coverage_complete')
        self.change('manifest.json', lambda m: m.update(source_timezone=None))
        self.assertEqual(self.run_intake().status, 'invalid')
        self.change('manifest.json', lambda m: m.pop('timestamp_convention'))
        self.assertEqual(self.run_intake().status, 'invalid')

    def test_offset_normalization_and_missing_timezone(self):
        rows = self.rows()
        from datetime import timezone
        for row in rows:
            row['timestamp'] = datetime.fromisoformat(row['timestamp']).astimezone(timezone.utc).isoformat()
        self.write_rows(rows)
        self.change('manifest.json', lambda m: m.update(source_timezone=None))
        self.assertEqual(self.run_intake().status, 'coverage_complete')
        self.change('manifest.json', lambda m: m.pop('timezone'))
        self.assertEqual(self.run_intake().status, 'invalid')

    def test_repeated_imports_are_immutable_and_observed_now_not_at_close(self):
        self.change('manifest.json', lambda m: m.update(claimed_acquired={'at':'2026-10-31T12:00:00+05:30','attribution':'User says prior download'}))
        first = self.run_intake(); first_dir = self.directory
        original = (first_dir / 'report.json').read_bytes(); normalized = self.normalized()
        second = self.run_intake(observed=OBSERVED + timedelta(hours=1))
        self.assertNotEqual(self.directory, first_dir)
        self.assertEqual((first_dir / 'report.json').read_bytes(), original)
        self.assertEqual(normalized['data'], self.normalized()['data'])
        self.assertNotEqual(first.imported_at, second.imported_at)
        self.assertEqual(normalized['provenance']['first_observed_at'], OBSERVED.isoformat())
        self.assertEqual(normalized['provenance']['manifest']['source_label'], 'Synthetic engineering fixture')
        self.assertEqual(normalized['provenance']['manifest']['dataset_nature'], 'synthetic_test')
        self.assertNotEqual(normalized['provenance']['claimed_acquired']['at'], normalized['provenance']['first_observed_at'])
        self.assertNotIn('available_at', json.dumps(normalized))

    def test_current_or_undated_assertions_never_verify_past_or_affect_replay(self):
        before = replay(load_dataset(), parse_timestamp('2026-10-30T09:35:00+05:30'))
        for day in [None, '2026-11-01']:
            self.change('manifest.json', lambda m: m['stock_list'].update(source_date=day, as_of_date=day, evidence=[]))
            result = self.run_intake()
            self.assertTrue(all(m.level == 'user_assertion' and not m.dated_review for m in result.membership))
            self.assertIn('eligibility_review_pending', result.gaps)
        self.assertEqual(before, replay(load_dataset(), parse_timestamp('2026-10-30T09:35:00+05:30')))

    def test_full_list_dedup_csv_unknown_mappings_and_no_extra_candle_requirement(self):
        (self.source / 'stocks.csv').write_text('symbol\n demo_alpha \nDEMO_ALPHA\nDEMO_BETA\nDEMO_GAMMA\nEXTRA\nUNKNOWN\n')
        self.change('manifest.json', lambda m: (m['stock_list'].update(file='stocks.csv'), m['instruments'].append(dict(source_symbol='EXTRA',symbol='EXTRA',exchange='NSE',instrument_type='equity',sample=False))))
        report = self.run_intake()
        self.assertEqual(report.list_duplicates, 1)
        self.assertEqual(report.universe_count, 5)
        self.assertEqual(report.unmapped_symbols, 1)
        self.assertEqual(sum(s.expected for s in report.series), 36)
        self.assertTrue(all(s.present == 9 for s in report.series))

    def test_index_and_equity_missing_and_zero_volume(self):
        rows = self.rows()
        rows[0]['volume'] = ''; rows[1]['volume'] = '0'; rows[28]['volume'] = '0'
        self.write_rows(rows)
        report = self.run_intake()
        bars = self.normalized()['data']['bars']
        def find(symbol, start):
            return next(b for b in bars if b['symbol'] == symbol and start in b['bar_start'])
        self.assertEqual(find('DEMO_ALPHA', '09:15')['volume_status'], 'missing')
        self.assertEqual(find('DEMO_ALPHA', '09:20')['volume'], 0)
        self.assertEqual(find('NIFTY50', '09:15')['volume_status'], 'not_applicable')
        self.assertEqual(find('NIFTY50', '09:20')['volume_status'], 'provider_zero')
        self.assertEqual(find('NIFTY50', '09:20')['raw_volume'], '0')
        self.assertEqual(sum(s.present for s in report.series), 36)
        self.assertIn('equity_volume_missing', report.gaps)

    def test_publication_precision_manual_reconciliation_and_missing_figures(self):
        self.assertEqual(self.run_intake().filing.publication_precision, 'exact')
        self.change('filing.json', lambda f: f.update(publication={'precision':'date_only','date':'2026-10-20'}, transcription_status='transcribed', reconciliation_reference=None))
        result = self.run_intake()
        self.assertEqual(result.filing.publication_precision, 'date_only')
        self.assertEqual(result.filing.reconciliation, 'transcribed')
        self.assertIn('filing_publication_partial', result.gaps)
        self.assertIsNone(self.normalized()['data']['filing']['publication']['timestamp'])
        self.assertIsNone(self.normalized()['data']['filing']['profit_attributable_to_owners'])
        self.change('filing.json', lambda f: f.update(publication={'precision':'unknown'}))
        self.assertEqual(self.run_intake().filing.publication_precision, 'unknown')
        self.change('filing.json', lambda f: f.update(publication={'precision':'exact','timestamp':'2026-10-20T10:00:00+05:30'}))
        self.assertEqual(self.run_intake().status, 'invalid')

    def test_filing_hash_and_impossible_time_orderings(self):
        original = json.loads((self.source / 'filing.json').read_text())
        for mutate in [lambda f: f.update(sha256='0'*64),
                       lambda f: f['publication'].update(timestamp='2026-11-02T10:00:00+05:30'),
                       lambda f: f.update(claimed_acquired={'at':'2026-10-19T10:00:00+05:30','attribution':'User claim'}),
                       lambda f: f.update(quarter_end='2026-12-31',publication={'precision':'unknown'}),
                       lambda f: f.update(publication={'precision':'date_only','date':'2026-09-01'})]:
            (self.source / 'filing.json').write_text(json.dumps(original))
            self.change('filing.json', mutate)
            self.assertEqual(self.run_intake().status, 'invalid')

    def test_optional_figures_complete_through_import_cli_and_api(self):
        original = json.loads((self.source / 'filing.json').read_text())
        names = ('revenue', 'profit_attributable_to_owners', 'diluted_eps')
        private = ROOT / 'private-data'
        private.mkdir(exist_ok=True)
        for variant in ('omitted', 'null', 'null_current'):
            with self.subTest(variant=variant), tempfile.TemporaryDirectory(dir=private) as output:
                filing = copy.deepcopy(original)
                for name in names:
                    filing.pop(name)
                if variant != 'omitted':
                    filing.update(dict.fromkeys(names))
                if variant == 'null_current':
                    filing['revenue'] = {**original['revenue'], 'current': None}
                (self.source / 'filing.json').write_text(json.dumps(filing))
                result = self.run_intake()
                self.assertEqual(result.status, 'coverage_complete')
                self.assertEqual(result.filing.figures_present, 0)
                self.assertEqual(result.gaps, [])
                normalized = self.normalized()['data']['filing']
                for name in names:
                    if name == 'revenue' and variant == 'null_current':
                        self.assertIsNone(normalized[name]['current'])
                        self.assertEqual(normalized[name]['prior'], original[name]['prior'])
                    else:
                        self.assertIsNone(normalized[name])
                    self.assertEqual(normalized['yoy'][name], {'value_pct': None, 'reason': 'missing_figures'})
                cli = subprocess.run([sys.executable, '-m', 'backend.app.intake', str(self.source),
                                      '--output-root', output], cwd=ROOT, capture_output=True, text=True)
                self.assertEqual(cli.returncode, 0, cli.stderr)
                report_file, = Path(output).glob('*/report.json')
                with patch.dict(os.environ, {'TRADE_COVERAGE_REPORT': str(report_file)}), TestClient(app) as client:
                    response = client.get('/api/data-coverage')
                    body = response.json()
                    self.assertEqual(body['state'], 'report')
                    self.assertEqual(body['report']['status'], 'coverage_complete')
                    self.assertEqual(body['report']['filing']['figures_present'], 0)
                    self.assertEqual(body['report']['gaps'], [])
                    self.assertNotIn('revenue', response.text)
                    self.assertNotIn('yoy', response.text)

    def test_supplied_malformed_figures_still_invalidate_intake(self):
        original = json.loads((self.source / 'filing.json').read_text())
        invalid = [{}, [], True, {'current': None},
                   {**original['revenue'], 'page_row_reference': ' '},
                   {**original['revenue'], 'unknown_field': 1}]
        for field in ('current', 'prior'):
            invalid.extend({**original['revenue'], field: value}
                           for value in ('100', 'NaN', True, float('nan'), float('inf'), -float('inf')))
        for figure in invalid:
            with self.subTest(figure=figure):
                self.change('filing.json', lambda f: f.update(revenue=figure))
                report = self.run_intake()
                self.assertEqual(report.status, 'invalid')
                self.assertFalse(report.schema_valid)
                self.assertIn('invalid_rows', report.gaps)
                self.assertNotIn('filing_figures_missing', report.gaps)

    def test_zero_figures_do_not_bypass_required_filing_or_reviews(self):
        self.change('filing.json', lambda f: f.update(revenue=None))
        originals = {p.name: p.read_bytes() for p in self.source.iterdir() if p.is_file()}
        cases = [
            ('filing metadata', lambda: (self.source / 'filing.json').unlink(), 'partial', 'filing_missing'),
            ('filing document', lambda: (self.source / 'filing.txt').unlink(), 'partial', 'filing_missing'),
            ('publication support', lambda: (self.source / 'publication.txt').unlink(), 'partial', 'filing_publication_partial'),
            ('publication precision', lambda: self.change('filing.json', lambda f: f.update(publication={'precision': 'unknown'})), 'partial', 'filing_publication_partial'),
            ('unreconciled', lambda: self.change('filing.json', lambda f: f.update(transcription_status='transcribed', reconciliation_reference=None)), 'partial', 'filing_reconciliation_pending'),
            ('reconciliation reference', lambda: self.change('filing.json', lambda f: f.update(reconciliation_reference=None)), 'invalid', 'invalid_rows'),
            ('filing source', lambda: self.change('filing.json', lambda f: f.update(source_url=None)), 'partial', 'filing_source_unknown'),
            ('source review', lambda: self.change('manifest.json', lambda m: m['source_review'].update(confirmed=False, reference=None)), 'partial', 'source_review_pending'),
            ('session review', lambda: self.change('manifest.json', lambda m: m['normal_session_review'].update(confirmed=False, reference=None)), 'partial', 'session_review_pending'),
            ('eligibility review', lambda: self.change('manifest.json', lambda m: m['stock_list']['evidence'][0]['review'].update(confirmed=False, reference=None)), 'partial', 'eligibility_review_pending'),
            ('candle interval', lambda: self.write_rows(self.rows()[1:]), 'partial', 'missing_bars'),
        ]
        for name, mutate, status, gap in cases:
            with self.subTest(requirement=name):
                for filename, raw in originals.items():
                    (self.source / filename).write_bytes(raw)
                mutate()
                report = self.run_intake()
                self.assertEqual(report.status, status)
                self.assertEqual(report.filing.figures_present, 0)
                self.assertIn(gap, report.gaps)
                self.assertNotIn('filing_figures_missing', report.gaps)
                if name == 'unreconciled':
                    self.assertEqual(report.filing.reconciliation, 'transcribed')

    def test_legacy_figure_gap_remains_readable_and_immutable_on_rerun(self):
        self.change('filing.json', lambda f: f.update(revenue=None))
        self.run_intake()
        # A disposable pre-correction report fixture, never a genuine historical report.
        legacy = copy.deepcopy(self.envelope)
        legacy['coverage'].update(status='partial', gaps=['filing_figures_missing'])
        legacy_path = self.root / 'legacy-report.json'
        legacy_raw = json.dumps(legacy).encode()
        legacy_path.write_bytes(legacy_raw)
        with patch.dict(os.environ, {'TRADE_COVERAGE_REPORT': str(legacy_path)}), TestClient(app) as client:
            body = client.get('/api/data-coverage').json()
            self.assertEqual(body['state'], 'report')
            self.assertEqual(body['report']['status'], 'partial')
            self.assertEqual(body['report']['gaps'], ['filing_figures_missing'])
        previous_dir = self.directory
        self.assertEqual(self.run_intake().status, 'coverage_complete')
        self.assertNotEqual(self.directory, previous_dir)
        self.assertEqual(legacy_path.read_bytes(), legacy_raw)

    def test_invalid_figure_counts_are_rejected_by_coverage_api(self):
        self.change('filing.json', lambda f: f.update(revenue=None))
        self.run_intake()
        report_file = self.root / 'count-test-report.json'
        for count in (-1, 4, 0.5, True, None, '0', float('nan'), float('inf')):
            with self.subTest(count=count):
                envelope = copy.deepcopy(self.envelope)
                envelope['coverage']['filing']['figures_present'] = count
                report_file.write_text(json.dumps(envelope))
                with patch.dict(os.environ, {'TRADE_COVERAGE_REPORT': str(report_file)}), TestClient(app) as client:
                    self.assertEqual(client.get('/api/data-coverage').json()['state'], 'invalid_report')

    def test_yoy_only_comparable_positive_denominator(self):
        self.run_intake()
        self.assertEqual(self.normalized()['data']['filing']['yoy']['revenue']['value_pct'], 25.0)
        original = json.loads((self.source / 'filing.json').read_text())
        for changes, reason in [({'prior':0.0},'nonpositive_prior_denominator'), ({'prior':-2.0},'nonpositive_prior_denominator'),
                                ({'prior_unit':'USD million'},'incomparable_units_or_periods'),
                                ({'prior_period_end':'2025-06-30'},'incomparable_units_or_periods'),
                                ({'prior_period_months':6},'incomparable_units_or_periods'),
                                ({'current':None},'missing_figures')]:
            (self.source / 'filing.json').write_text(json.dumps(original))
            self.change('filing.json', lambda f: f['revenue'].update(changes))
            self.run_intake()
            self.assertEqual(self.normalized()['data']['filing']['yoy']['revenue'], {'value_pct':None,'reason':reason})
        self.change('filing.json', lambda f: f.update(total_profit={'current':100.0}))
        self.assertEqual(self.run_intake().status, 'invalid')

    def test_missing_inputs_retention_pending_and_no_destructive_overwrite(self):
        self.change('manifest.json', lambda m: m.update(retention='unresolved',retention_note=None))
        result = self.run_intake()
        self.assertIn('retention_pending', result.gaps)
        self.assertEqual(self.envelope['provenance']['files'], {})
        self.assertFalse((self.directory / 'originals').exists())
        self.assertFalse((self.directory / 'normalized.json').exists())
        self.assertEqual(sum(s.present for s in result.series), 0)
        self.change('manifest.json', lambda m: m.update(retention='permitted',retention_note='Test inputs'))
        (self.source / 'candles.csv').unlink(); (self.source / 'filing.txt').unlink()
        report = self.run_intake()
        self.assertIn('candles_missing', report.gaps)
        self.assertIn('filing_missing', report.gaps)
        (self.source / 'manifest.json').unlink()
        self.assertIn('manifest_missing', self.run_intake().gaps)

    def test_document_hash_mismatch_and_wrong_effective_date_never_pass_review(self):
        self.change('manifest.json', lambda m: m['stock_list']['evidence'][0].update(effective_date='2026-11-01'))
        report = self.run_intake()
        self.assertEqual(report.status, 'partial')
        self.assertFalse(report.membership[0].dated_review)
        self.change('manifest.json', lambda m: m['stock_list']['evidence'][0].update(sha256='0'*64))
        self.assertEqual(self.run_intake().status, 'invalid')

    def test_path_traversal_symlinks_and_nonfinite_manifest_rejected(self):
        self.change('manifest.json', lambda m: m['stock_list']['evidence'][0].update(document='../private.txt'))
        self.assertEqual(self.run_intake().status, 'invalid')
        shutil.copy(ROOT / 'data/intake-example/manifest.json', self.source / 'manifest.json')
        (self.source / 'eligibility.txt').unlink()
        (self.source / 'eligibility.txt').symlink_to(ROOT / 'AGENTS.md')
        self.assertEqual(self.run_intake().status, 'invalid')
        self.assertNotIn('AGENTS.md', json.dumps(self.envelope))
        (self.source / 'manifest.json').write_text('{"schema_version":"local-intake-v1","source_date":NaN}')
        self.assertEqual(self.run_intake().status, 'invalid')

    def test_api_sanitizes_and_cannot_read_caller_paths_or_relabel_replay(self):
        self.run_intake()
        report_file = self.directory / 'report.json'
        for configured, state in [(None,'not_imported'), (str(report_file),'report'), (str(self.root / 'missing'),'invalid_report')]:
            with patch.dict(os.environ, {'TRADE_COVERAGE_REPORT': configured or ''}), TestClient(app) as client:
                response = client.get('/api/data-coverage', params={'path':str(ROOT/'AGENTS.md')})
                self.assertEqual(response.status_code,200)
                body = response.json()
                self.assertEqual(body['state'], state)
                self.assertNotIn(str(self.root), response.text)
                self.assertNotIn('originals',response.text)
                self.assertNotIn('sha256',response.text)
                self.assertNotIn('revenue',response.text)
                self.assertEqual(client.get('/api/demo').json()['mode'],'synthetic_demo')
                self.assertEqual(client.post('/api/data-coverage').status_code,405)
        original = json.loads(report_file.read_text())
        mutations = [lambda e:e.update(schema_version='future'), lambda e:e['coverage'].update(schema_version='future'),
                     lambda e:e['coverage'].pop('schema_version'),
                     lambda e:e['coverage']['series'][0].update(present=float('nan')),
                     lambda e:e['coverage']['series'][0].update(present=8),
                     lambda e:e['coverage'].update(source_label='/private/secret'),
                     lambda e:e['coverage'].update(raw_file='secret'),
                     lambda e:e['coverage']['filing'].update(symbol='NIFTY50'),
                     lambda e:e['coverage'].update(session_date=None),
                     lambda e:e['coverage']['membership'][0].update(dated_review=False)]
        for mutate in mutations:
            changed=copy.deepcopy(original); mutate(changed); report_file.write_text(json.dumps(changed))
            with patch.dict(os.environ, {'TRADE_COVERAGE_REPORT':str(report_file)}), TestClient(app) as client:
                self.assertEqual(client.get('/api/data-coverage').json()['state'],'invalid_report')

    def test_cli_exit_codes_ready_partial_invalid(self):
        private = ROOT / 'private-data'; private.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=private) as output:
            def execute():
                return subprocess.run([sys.executable,'-m','backend.app.intake',str(self.source),'--output-root',output],cwd=ROOT,capture_output=True,text=True)
            self.assertEqual(execute().returncode,0)
            (self.source/'candles.csv').unlink()
            self.assertEqual(execute().returncode,1)
            (self.source/'manifest.json').write_text('{broken')
            self.assertEqual(execute().returncode,2)
        result=subprocess.run([sys.executable,'-m','backend.app.intake',str(self.source),'--output-root',str(self.output)],cwd=ROOT,capture_output=True,text=True)
        self.assertEqual(result.returncode,2)


if __name__ == '__main__':
    unittest.main()
