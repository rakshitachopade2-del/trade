"""Bounded, offline import of one explicitly declared sample. Never feeds replay."""

import csv
import hashlib
import io
import json
import math
import re
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

from pydantic import ValidationError

from ..loader import IST
from .filing import normalize_filing, validate_times
from .report import Coverage
from .schema import Filing, Manifest

MAX_BYTES = 10 * 1024 * 1024
PARSER_VERSION = 'local-intake-v1'


def strict_json(raw: bytes):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError('duplicate JSON property')
            result[key] = value
        return result
    def constant(_):
        raise ValueError('nonfinite JSON number')
    return json.loads(raw, object_pairs_hook=pairs, parse_constant=constant)


def parse_model(model, raw):
    return model.model_validate_json(json.dumps(strict_json(raw), allow_nan=False))


class Intake:
    def __init__(self, directory: Path, observed: datetime):
        self.directory = directory.resolve()
        self.observed = observed
        self.originals: dict[str, bytes] = {}
        self.errors: list[dict] = []
        self.gaps: set[str] = set()
        self.bars: list[dict] = []
        self.stock_symbols: list[str] = []
        self.eligibility: list[dict] = []
        self.filing = None
        self.report = dict(
            schema_version='coverage-v1', parser_version=PARSER_VERSION, status='partial',
            dataset_id=None, dataset_nature=None, source_label=None, session_date=None,
            imported_at=observed.isoformat(), stock_count=0, benchmark=None, series=[], membership=[],
            universe_count=0, list_duplicates=0, unmapped_symbols=0, invalid_rows=0,
            outside_window=0, duplicate_rows=0, schema_valid=True, source_review='pending',
            session_review='pending', price_adjustment='unknown', source_dates_known=False,
            retention='unresolved', filing={'status': 'not_imported'}, gaps=[])

    def error(self, file: str, row: int | None, message: str):
        # Only fixed diagnostics, never raw row values or absolute paths.
        self.errors.append({'file': file, 'row': row, 'message': message})

    def read(self, filename: str) -> bytes | None:
        if filename in self.originals:
            return self.originals[filename]
        path = self.directory / filename
        if path.is_symlink() or path.parent.resolve() != self.directory:
            self.error(filename, None, 'Expected a regular file directly inside the input directory; symlinks are not accepted.')
            return None
        try:
            with path.open('rb') as handle:
                raw = handle.read(MAX_BYTES + 1)
            if len(raw) > MAX_BYTES:
                self.error(filename, None, 'File exceeds the 10 MiB input limit.')
                return None
        except FileNotFoundError:
            return None
        except OSError:
            self.error(filename, None, 'Cannot read this input file.')
            return None
        self.originals[filename] = raw
        return raw

    def rows(self, filename, raw, fields):
        try:
            reader = csv.DictReader(io.StringIO(raw.decode('utf-8-sig'), newline=''), strict=True)
            headers = reader.fieldnames or []
            if len(set(headers)) != len(headers) or set(headers) != set(fields):
                self.error(filename, 1, 'Duplicate, missing or unsupported CSV headers; use the documented schema.')
                return
            for row in reader:
                if None in row or any(value is None for value in row.values()):
                    self.error(filename, reader.line_num, 'Column count does not match the header.')
                    if filename == 'candles.csv':
                        self.report['invalid_rows'] += 1
                    continue
                yield reader.line_num, row
        except (UnicodeError, csv.Error):
            self.error(filename, None, 'Expected well-formed UTF-8 CSV.')

    def execute(self):
        raw = self.read('manifest.json')
        if raw is None:
            self.gaps.add('manifest_missing')
            return self.finish()
        try:
            m = parse_model(Manifest, raw)
        except (ValueError, TypeError, OverflowError, RecursionError):
            self.error('manifest.json', None, 'Invalid manifest: check schema, explicit timezone/convention and unique instrument mappings.')
            self.gaps.add('manifest_invalid')
            return self.finish()
        self.manifest = m
        if m.claimed_acquired and m.claimed_acquired.at > self.observed:
            self.error('manifest.json', None, 'Claimed acquisition cannot be after the actual import.')
        if m.session_date > self.observed.astimezone(IST).date():
            self.error('manifest.json', None, 'Sample session cannot be after the actual import.')
        start = datetime.fromisoformat(f'{m.session_date}T09:15:00').replace(tzinfo=IST)
        self.expected = [start + timedelta(minutes=5 * i) for i in range(9)]
        self.selected = {i.symbol: i for i in m.instruments if i.sample}
        self.mapping = {i.source_symbol: i for i in m.instruments}
        self.report.update(dataset_id=m.dataset_id, dataset_nature=m.dataset_nature, source_label=m.source_label,
                           session_date=m.session_date.isoformat(), stock_count=3, benchmark='NIFTY50',
                           price_adjustment=m.price_adjustment, source_dates_known=m.source_date is not None or m.as_of_date is not None,
                           source_review='manual_confirmed' if m.source_review.confirmed else 'pending',
                           session_review='manual_confirmed' if m.normal_session_review.confirmed else 'pending', retention=m.retention)
        self.report['series'] = [dict(symbol=i.symbol, instrument_type=i.instrument_type, expected=9, present=0,
                                      missing=[t.strftime('%H:%M') for t in self.expected], duplicates=0,
                                      outside_window=0, missing_volume=0) for i in self.selected.values()]
        self.report['membership'] = [dict(symbol=i.symbol, level='unknown', dated_review=False)
                                     for i in self.selected.values() if i.instrument_type == 'equity']
        for condition, gap in [(not m.source_label, 'source_unknown'), (not self.report['source_dates_known'], 'source_dates_unknown'),
                               (m.price_adjustment == 'unknown', 'adjustment_unknown'),
                               (not m.source_review.confirmed, 'source_review_pending'),
                               (not m.normal_session_review.confirmed, 'session_review_pending')]:
            if condition:
                self.gaps.add(gap)
        if m.retention != 'permitted':
            self.gaps.update(['retention_pending', 'missing_bars', 'stock_list_missing', 'eligibility_review_pending', 'filing_missing'])
            # Do not read, hash or copy provider data while retention is unresolved.
            self.originals.clear()
            return self.finish()
        self.read_stocks(m)
        self.read_candles(m)
        self.read_filing(m)
        return self.finish()

    def read_stocks(self, m):
        spec = m.stock_list
        raw = self.read(spec.file) if spec else None
        if raw is None:
            self.gaps.add('stock_list_missing')
        else:
            if spec.file == 'stocks.csv':
                entries = [(row, data['symbol']) for row, data in self.rows(spec.file, raw, ['symbol'])]
            else:
                try:
                    entries = list(enumerate(raw.decode('utf-8-sig').splitlines(), 1))
                except UnicodeError:
                    self.error(spec.file, None, 'Expected UTF-8 text.')
                    entries = []
            seen = set()
            recognized = {i.symbol for i in m.instruments if i.instrument_type == 'equity'}
            for row, value in entries:
                symbol = value.strip().upper()
                if not symbol:
                    continue
                if not re.fullmatch(r'[A-Z0-9][A-Z0-9&_.-]{0,29}', symbol):
                    self.error(spec.file, row, 'Expected an NSE symbol, not a company name or ambiguous identifier.')
                    continue
                if symbol in seen:
                    self.report['list_duplicates'] += 1
                else:
                    seen.add(symbol)
                    if symbol not in recognized:
                        self.report['unmapped_symbols'] += 1
            self.stock_symbols = sorted(seen)
            self.report['universe_count'] = len(seen)
            if not seen:
                self.gaps.add('stock_list_missing')
            if self.report['unmapped_symbols']:
                self.gaps.add('stock_list_unmapped')
            for member in self.report['membership']:
                if member['symbol'] in seen:
                    member['level'] = 'user_assertion'
        evidence_by_symbol = {}
        for evidence in spec.evidence if spec else []:
            if evidence.symbol not in {i.symbol for i in m.instruments if i.instrument_type == 'equity'} or evidence.symbol in evidence_by_symbol:
                self.error('manifest.json', None, 'Evidence symbol is unmapped or has ambiguous duplicate reviews.')
                continue
            evidence_by_symbol[evidence.symbol] = evidence
            document = self.read(evidence.document)
            if document is None:
                self.gaps.add('eligibility_review_pending')
                continue
            digest = hashlib.sha256(document).hexdigest()
            if digest != evidence.sha256:
                self.error('manifest.json', None, 'Eligibility document hash does not match the supplied bytes.')
                continue
            self.eligibility.append(evidence.model_dump(mode='json'))
            for member in self.report['membership']:
                if member['symbol'] == evidence.symbol:
                    member['level'] = 'supporting_evidence'
                    member['dated_review'] = evidence.review.confirmed and evidence.effective_date == m.session_date
        if not all(member['dated_review'] for member in self.report['membership']):
            self.gaps.add('eligibility_review_pending')

    def timestamp(self, value, m):
        try:
            if not re.fullmatch(r'\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}(?::\d{2}(?:\.\d{1,6})?)?(?:Z|[+-]\d{2}:\d{2})?', value.strip()):
                raise ValueError()
            at = datetime.fromisoformat(value.strip())
            if at.tzinfo is None or at.utcoffset() is None:
                if not m.source_timezone:
                    raise ValueError()
                zone = ZoneInfo(m.source_timezone)
                # DST gaps and folds need an explicit offset, never guessed fold=0.
                a, b = at.replace(tzinfo=zone, fold=0), at.replace(tzinfo=zone, fold=1)
                if a.utcoffset() != b.utcoffset() or a.astimezone(timezone.utc).astimezone(zone).replace(tzinfo=None) != at:
                    raise ValueError()
                at = a
            return at.astimezone(IST)
        except (ValueError, OverflowError):
            raise ValueError('Timestamp needs a valid explicit offset or unambiguous declared source timezone.') from None

    def read_candles(self, m):
        raw = self.read('candles.csv')
        series = {s['symbol']: s for s in self.report['series']}
        seen, conflicts = {}, set()
        if raw is None:
            self.gaps.add('candles_missing')
        else:
            for line, row in self.rows('candles.csv', raw, ['symbol', 'timestamp', 'open', 'high', 'low', 'close', 'volume']):
                try:
                    instrument = self.mapping.get(row['symbol'].strip().upper())
                    if instrument is None:
                        self.gaps.add('mapping_unknown')
                        raise ValueError('Source symbol has no explicit instrument mapping.')
                    event = self.timestamp(row['timestamp'], m)
                    start = event if m.timestamp_convention == 'bar_start' else event - timedelta(minutes=5)
                    end = start + timedelta(minutes=5)
                    if start.date() != m.session_date:
                        raise ValueError('Candle belongs to a different session date.')
                    if start.second or start.microsecond or start.minute % 5:
                        raise ValueError('Candle is not aligned to an exact five-minute interval.')
                    if end > self.observed or (m.claimed_acquired and end > m.claimed_acquired.at):
                        raise ValueError('Completed candle ends after import or claimed acquisition.')
                    try:
                        prices = [float(row[field]) for field in ('open', 'high', 'low', 'close')]
                    except ValueError:
                        raise ValueError('OHLC requires finite positive numbers.') from None
                    opening, high, low, close = prices
                    if not all(math.isfinite(p) and p > 0 for p in prices) or not low <= opening <= high or not low <= close <= high:
                        raise ValueError('OHLC requires finite positive values with low <= open/close <= high.')
                    raw_volume = row['volume']
                    volume_text = raw_volume.strip()
                    if not volume_text:
                        volume = None
                        volume_status = 'not_applicable' if instrument.instrument_type == 'spot_index' else 'missing'
                    else:
                        if not re.fullmatch(r'\d+', volume_text) or len(volume_text) > 16:
                            raise ValueError('Volume must be empty or a non-negative integer of at most 16 digits.')
                        volume = int(volume_text)
                        volume_status = 'provider_zero' if volume == 0 else 'reported'
                    bar = dict(symbol=instrument.symbol, source_symbol=instrument.source_symbol,
                               source_timestamp=row['timestamp'], event_at=event.isoformat(),
                               bar_start=start.isoformat(), bar_end=end.isoformat(), open=opening, high=high,
                               low=low, close=close, volume=volume, raw_volume=raw_volume, volume_status=volume_status)
                    key = (instrument.symbol, start)
                    # Compare normalized meaning; retain the first raw provider fields deterministically.
                    signature = (opening, high, low, close, volume, volume_status)
                    if key in seen:
                        if seen[key][0] != signature:
                            conflicts.add(key)
                            raise ValueError('Conflicting duplicate candle; no version is accepted for coverage.')
                        self.report['duplicate_rows'] += 1
                        if instrument.sample:
                            series[instrument.symbol]['duplicates'] += 1
                    else:
                        seen[key] = (signature, bar)
                    if not instrument.sample or start not in self.expected:
                        self.report['outside_window'] += 1
                        if instrument.sample:
                            series[instrument.symbol]['outside_window'] += 1
                except (ValueError, OverflowError) as exc:
                    self.report['invalid_rows'] += 1
                    self.error('candles.csv', line, str(exc))
        for (symbol, start), (_, bar) in sorted(seen.items()):
            if (symbol, start) in conflicts:
                continue
            bar['in_sample'] = symbol in self.selected and start in self.expected
            self.bars.append(bar)
            if bar['in_sample']:
                entry = series[symbol]
                entry['present'] += 1
                entry['missing'].remove(start.strftime('%H:%M'))
                if bar['volume_status'] == 'missing':
                    entry['missing_volume'] += 1
        if any(s['missing'] for s in series.values()):
            self.gaps.add('missing_bars')
        if any(s['missing_volume'] for s in series.values()):
            self.gaps.add('equity_volume_missing')

    def read_filing(self, m):
        raw = self.read(m.filing) if m.filing else None
        if raw is None:
            self.gaps.add('filing_missing')
            return
        try:
            filing = parse_model(Filing, raw)
            if filing.symbol not in {i.symbol for i in self.selected.values() if i.instrument_type == 'equity'}:
                raise ValueError('Filing must belong to a selected equity.')
            validate_times(filing, self.observed)
            document = self.read(filing.document)
            if document is None:
                self.gaps.add('filing_missing')
                return
            digest = hashlib.sha256(document).hexdigest()
            if filing.sha256 and filing.sha256 != digest:
                raise ValueError('Filing document hash does not match.')
            precision = filing.publication.precision
            if precision == 'exact' and self.read(filing.publication.record_document) is None:
                self.gaps.add('filing_publication_partial')
                # Retain supplied exact metadata privately, but missing support cannot pass coverage.
            self.filing = normalize_filing(filing, digest)
            count = sum(getattr(filing, name) is not None and getattr(filing, name).current is not None
                        for name in ('revenue', 'profit_attributable_to_owners', 'diluted_eps'))
            self.report['filing'] = dict(status='imported', symbol=filing.symbol, publication_precision=precision,
                                         reconciliation=filing.transcription_status, figures_present=count,
                                         source_known=filing.source_url is not None)
            for condition, gap in [(precision != 'exact', 'filing_publication_partial'),
                                   (filing.transcription_status != 'reconciled', 'filing_reconciliation_pending'),
                                   (not count, 'filing_figures_missing'), (not filing.source_url, 'filing_source_unknown')]:
                if condition:
                    self.gaps.add(gap)
        except (ValidationError, ValueError, TypeError, OverflowError, RecursionError):
            self.error('filing.json', None, 'Invalid filing metadata: check schema, symbol, hashes, publication precision and time ordering.')

    def finish(self):
        if self.errors:
            self.gaps.add('invalid_rows')
        self.report['schema_valid'] = not self.errors
        self.report['gaps'] = sorted(self.gaps)
        self.report['status'] = 'invalid' if self.errors else 'partial' if self.gaps else 'coverage_complete'
        return Coverage.model_validate_json(json.dumps(self.report, allow_nan=False))


def run_import(directory: Path, output_root: Path, *, observed: datetime | None = None) -> tuple[Path, Coverage]:
    observed = observed or datetime.now(timezone.utc)
    if observed.tzinfo is None or observed.utcoffset() is None:
        raise ValueError('import clock must be timezone aware')
    run = Intake(directory, observed)
    report = run.execute()
    output_root.mkdir(parents=True, exist_ok=True)
    destination = output_root / (observed.astimezone(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ') + '-' + uuid.uuid4().hex[:12])
    destination.mkdir(mode=0o700)  # exclusive: never overwrite an earlier import
    permitted = getattr(run, 'manifest', None) is not None and run.manifest.retention == 'permitted'
    provenance = {
        'run_id': destination.name, 'first_observed_at': observed.isoformat(), 'parser_version': PARSER_VERSION,
        'files': {name: hashlib.sha256(raw).hexdigest() for name, raw in sorted(run.originals.items())} if permitted else {},
        'claimed_acquired': run.manifest.claimed_acquired.model_dump(mode='json') if permitted and run.manifest.claimed_acquired else None,
        'manifest': run.manifest.model_dump(mode='json') if permitted else None,
        'observation_scope': 'This run obtained these bytes at first_observed_at. No historical availability is inferred.',
    }
    envelope = {'schema_version': 'intake-run-v1', 'coverage': report.model_dump(mode='json'),
                'provenance': provenance, 'diagnostics': run.errors}
    (destination / 'report.json').write_text(json.dumps(envelope, indent=2, allow_nan=False) + '\n')
    (destination / 'report.txt').write_text(human_report(report, run.errors))
    if permitted:
        originals = destination / 'originals'
        originals.mkdir(mode=0o700)
        for filename, raw in run.originals.items():
            (originals / filename).write_bytes(raw)
        normalized = {'schema_version': PARSER_VERSION, 'provenance': provenance,
                      'data': {'bars': run.bars, 'stock_symbols': run.stock_symbols,
                               'stock_list_metadata': run.manifest.stock_list.model_dump(mode='json') if run.manifest.stock_list else None,
                               'eligibility_evidence': run.eligibility, 'filing': run.filing}}
        (destination / 'normalized.json').write_text(json.dumps(normalized, indent=2, allow_nan=False) + '\n')
    return destination, report


def human_report(report, errors):
    lines = [f'Data coverage: {report.status}', f'Nature: {report.dataset_nature or "unknown"}',
             f'Dataset: {report.dataset_id or "unknown"}; session: {report.session_date or "unknown"}',
             f'Imported: {report.imported_at.isoformat()}',
             f'Source: {report.source_label or "unknown"}; review: {report.source_review}; adjustment: {report.price_adjustment}',
             f'Schema valid: {report.schema_valid}; normal-session review: {report.session_review}; retention: {report.retention}',
             f'Universe: {report.universe_count}; list duplicates: {report.list_duplicates}; unmapped list symbols: {report.unmapped_symbols}',
             'Separate from synthetic research. Coverage does not establish source accuracy, historical availability or profitable trading.']
    for series in report.series:
        lines.append(f'{series.symbol} ({series.instrument_type}): {series.present}/{series.expected}; missing starts: {", ".join(series.missing) or "none"}; duplicate rows: {series.duplicates}; outside sample: {series.outside_window}')
    lines.extend(f'{m.symbol} membership: {m.level}; dated manual review: {m.dated_review}' for m in report.membership)
    lines.append(f'Filing: {report.filing.status}; publication: {report.filing.publication_precision}; transcription: {report.filing.reconciliation}')
    lines.append('Gaps: ' + (', '.join(report.gaps) or 'none; required reviews are manual assertions'))
    lines.extend(f'{e["file"]}:row {e["row"] or "?"}: {e["message"]}' for e in errors)
    return '\n'.join(lines) + '\n'
