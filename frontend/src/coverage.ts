export const gapMessages = {
  manifest_missing: 'Add manifest.json to the input directory.',
  manifest_invalid: 'Correct the manifest schema and explicit instrument mappings.',
  retention_pending: 'Local acquisition/retention permission is unresolved; provider files were not read or retained.',
  candles_missing: 'Supply the permitted candles.csv export.',
  invalid_rows: 'Correct malformed or contradictory inputs using the private report diagnostics.',
  missing_bars: 'Supply missing intervals; prices are never filled or interpolated.',
  mapping_unknown: 'Add explicit mappings for candle source symbols.',
  source_unknown: 'Record the candle source label.',
  source_dates_unknown: 'Record a known source or as-of date.',
  adjustment_unknown: 'Confirm the price-adjustment convention.',
  source_review_pending: 'Source review is pending; structural validity is not source verification.',
  session_review_pending: 'Confirm the declared session had a normal 09:15 opening, with a reference.',
  stock_list_missing: 'Supply a stock list with optional source and date.',
  stock_list_unmapped: 'Review unrecognized stock-list symbols and add explicit mappings.',
  eligibility_review_pending: 'Dated stock-options documentary review remains pending for the sample.',
  filing_missing: 'Import one filing document with manually entered metadata.',
  filing_publication_partial: 'Exact publication-time coverage needs a supported dissemination timestamp.',
  filing_reconciliation_pending: 'Manually reconcile the filing transcription against source pages.',
  filing_figures_missing: 'Legacy report: optional figures no longer block completion. Rerun the original inputs to generate a new report; preserve this report.',
  filing_source_unknown: 'Record the filing source URL in its private metadata.',
  equity_volume_missing: 'Equity volume is missing; zero volume is preserved separately.',
} as const;

type Gap = keyof typeof gapMessages;
export interface CoverageReport {
  schema_version: 'coverage-v1'; parser_version: 'local-intake-v1';
  status: 'partial' | 'invalid' | 'coverage_complete';
  dataset_id: string | null; dataset_nature: 'synthetic_test' | 'user_import' | null;
  source_label: string | null; session_date: string | null; imported_at: string;
  stock_count: number; benchmark: 'NIFTY50' | null;
  series: { symbol: string; instrument_type: 'equity' | 'spot_index'; expected: number; present: number; missing: string[]; duplicates: number; outside_window: number; missing_volume: number }[];
  membership: { symbol: string; level: 'unknown' | 'user_assertion' | 'supporting_evidence'; dated_review: boolean }[];
  universe_count: number; list_duplicates: number; unmapped_symbols: number; invalid_rows: number; outside_window: number; duplicate_rows: number;
  schema_valid: boolean; source_review: 'pending' | 'manual_confirmed'; session_review: 'pending' | 'manual_confirmed';
  price_adjustment: 'adjusted' | 'unadjusted' | 'unknown'; source_dates_known: boolean; retention: 'permitted' | 'unresolved';
  filing: { status: 'not_imported' | 'imported'; symbol: string | null; publication_precision: 'exact' | 'date_only' | 'unknown'; reconciliation: 'unreviewed' | 'transcribed' | 'reconciled'; figures_present: number; source_known: boolean };
  gaps: Gap[];
}
export type CoverageResponse = { api_version: 'coverage-api-v1'; state: 'not_imported' | 'invalid_report'; report: null }
  | { api_version: 'coverage-api-v1'; state: 'report'; report: CoverageReport };

const object = (v: unknown): v is Record<string, unknown> => typeof v === 'object' && v !== null && !Array.isArray(v);
const count = (v: unknown): v is number => typeof v === 'number' && Number.isSafeInteger(v) && v >= 0;
const choice = (v: unknown, allowed: string[]) => typeof v === 'string' && allowed.includes(v);
const symbol = (v: unknown): v is string => typeof v === 'string' && /^[A-Z0-9][A-Z0-9&_.-]{0,29}$/.test(v);
const label = (v: unknown) => v === null || typeof v === 'string' && /^[A-Za-z0-9][A-Za-z0-9 ._()-]{0,99}$/.test(v);
const date = (v: unknown) => v === null || typeof v === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(v) && Number.isFinite(Date.parse(v)) && new Date(v).toISOString().startsWith(v);

function validReport(r: unknown): r is CoverageReport {
  if (!object(r) || r.schema_version !== 'coverage-v1' || r.parser_version !== 'local-intake-v1'
    || !choice(r.status, ['partial', 'invalid', 'coverage_complete']) || !label(r.dataset_id) || !label(r.source_label)
    || !(r.dataset_nature === null || choice(r.dataset_nature, ['synthetic_test', 'user_import'])) || !date(r.session_date)
    || typeof r.imported_at !== 'string' || !/(Z|[+-]\d{2}:\d{2})$/.test(r.imported_at) || !Number.isFinite(Date.parse(r.imported_at))
    || !['stock_count', 'universe_count', 'list_duplicates', 'unmapped_symbols', 'invalid_rows', 'outside_window', 'duplicate_rows'].every(k => count(r[k]))
    || !choice(r.source_review, ['pending', 'manual_confirmed']) || !choice(r.session_review, ['pending', 'manual_confirmed'])
    || !choice(r.price_adjustment, ['adjusted', 'unadjusted', 'unknown']) || !choice(r.retention, ['permitted', 'unresolved'])
    || typeof r.source_dates_known !== 'boolean' || typeof r.schema_valid !== 'boolean' || r.schema_valid === (r.status === 'invalid')
    || !Array.isArray(r.gaps) || r.gaps.length > 30 || !r.gaps.every(g => typeof g === 'string' && Object.hasOwn(gapMessages, g))
    || !Array.isArray(r.series) || r.series.length > 4 || !Array.isArray(r.membership) || r.membership.length > 3) return false;
  if (!r.series.every(s => object(s) && symbol(s.symbol) && choice(s.instrument_type, ['equity', 'spot_index'])
    && s.expected === 9 && count(s.present) && s.present <= 9 && Array.isArray(s.missing)
    && s.missing.every(t => typeof t === 'string' && /^09:(15|20|25|30|35|40|45|50|55)$/.test(t))
    && new Set(s.missing).size === s.missing.length && s.present + s.missing.length === 9
    && count(s.duplicates) && count(s.outside_window) && count(s.missing_volume) && s.missing_volume <= s.present)) return false;
  if (!r.membership.every(m => object(m) && symbol(m.symbol) && choice(m.level, ['unknown', 'user_assertion', 'supporting_evidence'])
    && typeof m.dated_review === 'boolean' && (!m.dated_review || m.level === 'supporting_evidence'))) return false;
  const series = r.series as CoverageReport['series'];
  const members = r.membership as CoverageReport['membership'];
  const equities = series.filter(s => s.instrument_type === 'equity');
  if (new Set(r.gaps).size !== r.gaps.length || (r.invalid_rows !== 0 && r.status !== 'invalid')
    || (r.outside_window as number) < series.reduce((sum, s) => sum + s.outside_window, 0)
    || (r.duplicate_rows as number) < series.reduce((sum, s) => sum + s.duplicates, 0)) return false;
  if (series.length ? (series.length !== 4 || new Set(series.map(s => s.symbol)).size !== 4 || equities.length !== 3
    || !r.dataset_id || !r.dataset_nature || !r.session_date
    || series.find(s => s.instrument_type === 'spot_index')?.symbol !== 'NIFTY50' || r.stock_count !== 3 || r.benchmark !== 'NIFTY50'
    || members.length !== 3 || new Set(members.map(m => m.symbol)).size !== 3 || !members.every(m => equities.some(s => s.symbol === m.symbol)))
    : r.stock_count !== 0 || r.benchmark !== null || members.length !== 0) return false;
  const f = r.filing;
  if (!object(f) || !choice(f.status, ['not_imported', 'imported']) || !(f.symbol === null || symbol(f.symbol))
    || !choice(f.publication_precision, ['exact', 'date_only', 'unknown']) || !choice(f.reconciliation, ['unreviewed', 'transcribed', 'reconciled'])
    || !count(f.figures_present) || f.figures_present > 3 || typeof f.source_known !== 'boolean') return false;
  if (f.status === 'not_imported' ? (f.symbol !== null || f.publication_precision !== 'unknown' || f.reconciliation !== 'unreviewed' || f.figures_present !== 0 || f.source_known) : !symbol(f.symbol)) return false;
  if (f.status === 'imported' && !equities.some(s => s.symbol === f.symbol)) return false;
  if (r.status !== 'coverage_complete') return r.gaps.length > 0;
  return r.gaps.length === 0 && series.length === 4 && series.every(s => s.present === 9 && (s.instrument_type !== 'equity' || s.missing_volume === 0))
    && r.invalid_rows === 0 && r.unmapped_symbols === 0 && members.every(m => m.dated_review)
    && r.source_review === 'manual_confirmed' && r.session_review === 'manual_confirmed' && r.price_adjustment !== 'unknown'
    && r.source_dates_known && r.retention === 'permitted' && !!r.source_label && !!r.dataset_id && !!r.dataset_nature && !!r.session_date
    && f.status === 'imported' && f.publication_precision === 'exact' && f.reconciliation === 'reconciled' && f.source_known;
}

export async function getCoverage(signal: AbortSignal): Promise<CoverageResponse> {
  const response = await fetch('/api/data-coverage', { signal, headers: { Accept: 'application/json' } });
  if (!response.ok) throw new Error(`Coverage API returned HTTP ${response.status}. Check the local backend and retry.`);
  let value: unknown;
  try { value = await response.json(); } catch { throw new Error('Coverage API returned unreadable data. No coverage result is displayed.'); }
  if (!object(value) || value.api_version !== 'coverage-api-v1'
    || !(value.state === 'report' ? validReport(value.report) : choice(value.state, ['not_imported', 'invalid_report']) && value.report === null)) {
    throw new Error('Coverage API returned an incompatible or malformed report. No coverage result is displayed.');
  }
  return value as unknown as CoverageResponse;
}
