import type { DemoConfig, Replay } from './types';

async function getJson(path: string, signal: AbortSignal): Promise<unknown> {
  const response = await fetch(path, { signal, headers: { Accept: 'application/json' } });
  if (!response.ok) {
    throw new Error(`Research API returned HTTP ${response.status}. Check that the local API is running, then retry.`);
  }
  try { return await response.json(); }
  catch { throw new Error('The research API returned an unreadable response. No results have been displayed.'); }
}

function object(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null;
}

function timestamp(value: unknown): value is string {
  return typeof value === 'string' && /(?:Z|[+-]\d{2}:\d{2})$/.test(value) && Number.isFinite(Date.parse(value));
}

function finiteOrNull(value: unknown): boolean {
  return value === null || typeof value === 'number' && Number.isFinite(value);
}

function stringArray(value: unknown): value is string[] {
  return Array.isArray(value) && value.every((entry) => typeof entry === 'string');
}

function validCandidate(value: unknown, asOf: string): boolean {
  if (!object(value) || typeof value.symbol !== 'string' || typeof value.name !== 'string'
    || typeof value.sector !== 'string' || typeof value.state !== 'string' || !['qualified', 'watching', 'blocked'].includes(value.state)
    || typeof value.eligibility !== 'string' || !['eligible', 'ineligible', 'unknown'].includes(value.eligibility)
    || typeof value.fundamentals_status !== 'string' || !['available', 'unknown'].includes(value.fundamentals_status)
    || value.contract_status !== 'not_evaluated' || !stringArray(value.reasons) || !stringArray(value.reason_codes)
    || !Array.isArray(value.bars) || !Array.isArray(value.evidence)) return false;
  if (value.state === 'qualified') {
    if (typeof value.rank !== 'number' || !Number.isInteger(value.rank) || value.rank < 1) return false;
  } else if (value.rank !== null) return false;
  if (!['last_price', 'opening_range_high', 'opening_range_low', 'return_pct', 'benchmark_return_pct', 'relative_return_pct'].every((key) => finiteOrNull(value[key]))) return false;
  const cutoff = Date.parse(asOf);
  if (value.last_bar_end !== null && (!timestamp(value.last_bar_end) || Date.parse(value.last_bar_end) > cutoff)) return false;
  const bars = value.bars;
  if (!bars.every((bar, index) => object(bar) && timestamp(bar.bar_end) && Date.parse(bar.bar_end) <= cutoff
    && typeof bar.close === 'number' && Number.isFinite(bar.close)
    && (index === 0 || object(bars[index - 1]) && timestamp(bars[index - 1].bar_end) && Date.parse(bar.bar_end) > Date.parse(bars[index - 1].bar_end)))) return false;
  return value.evidence.every((item) => object(item)
    && ['id', 'kind', 'title', 'summary', 'period', 'source'].every((key) => typeof item[key] === 'string')
    && (item.source_url === null || typeof item.source_url === 'string')
    && timestamp(item.published_at) && timestamp(item.available_at)
    && Date.parse(item.published_at) <= Date.parse(item.available_at) && Date.parse(item.available_at) <= cutoff);
}

export async function getDemo(signal: AbortSignal): Promise<DemoConfig> {
  const result = await getJson('/api/demo', signal);
  if (!object(result) || result.mode !== 'synthetic_demo' || !Array.isArray(result.replay_times)
    || !result.replay_times.length || !result.replay_times.every(timestamp)
    || typeof result.default_as_of !== 'string' || !result.replay_times.includes(result.default_as_of)
    || typeof result.label !== 'string' || typeof result.source !== 'string') {
    throw new Error('The API did not provide a valid synthetic replay configuration. No fallback data is used.');
  }
  return result as unknown as DemoConfig;
}

export async function getReplay(asOf: string, signal: AbortSignal): Promise<Replay> {
  const result = await getJson(`/api/replay?as_of=${encodeURIComponent(asOf)}`, signal);
  if (!object(result) || result.mode !== 'synthetic_demo' || !timestamp(result.as_of)
    || Date.parse(result.as_of) !== Date.parse(asOf) || typeof result.rule_version !== 'string'
    || typeof result.source !== 'string' || !object(result.summary) || !Array.isArray(result.candidates)) {
    throw new Error('The API response does not match the selected synthetic replay. No results have been displayed.');
  }
  const summary = result.summary;
  if (!['total', 'qualified', 'watching', 'blocked'].every((key) => typeof summary[key] === 'number' && Number.isInteger(summary[key]) && (summary[key] as number) >= 0)
    || !result.candidates.every((candidate) => validCandidate(candidate, asOf))) {
    throw new Error('The API returned incomplete or invalid research data. No results have been displayed.');
  }
  const candidates = result.candidates as Record<string, unknown>[];
  if (new Set(candidates.map((candidate) => candidate.symbol)).size !== candidates.length
    || summary.total !== candidates.length
    || !['qualified', 'watching', 'blocked'].every((state) => summary[state] === candidates.filter((candidate) => candidate.state === state).length)) {
    throw new Error('The API returned inconsistent research counts. No results have been displayed.');
  }
  return result as unknown as Replay;
}
