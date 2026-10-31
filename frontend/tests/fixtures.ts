import type { Candidate, DemoConfig, Evidence, Replay } from '../src/types';

export const times = [
  '2026-10-30T09:30:00+05:30',
  '2026-10-30T09:35:00+05:30',
  '2026-10-30T09:40:00+05:30',
];

export const demo: DemoConfig = {
  mode: 'synthetic_demo',
  label: 'Synthetic demo data — not current market data',
  source: 'Bundled synthetic fixtures',
  replay_times: times,
  default_as_of: times[1],
};

const lateEvidence: Evidence = {
  id: 'beta-results', kind: 'quarterly_result', title: 'Beta result available at 09:40',
  summary: 'Fictional financial evidence for the replay.', period: 'DEMO quarter',
  source: 'Synthetic fixture', source_url: null,
  published_at: '2026-10-30T09:37:00+05:30', available_at: times[2],
};

export function replayAt(asOf: string): Replay {
  const qualified = asOf !== times[0];
  const candidates: Candidate[] = ['ALPHA', 'BETA', 'GAMMA', 'DELTA', 'EPSILON'].map((symbol, index) => ({
    symbol: `DEMO_${symbol}`, name: `${symbol[0]}${symbol.slice(1).toLowerCase()} Industries (fictional)`,
    sector: 'Industrials', rank: index === 0 && qualified ? 1 : null,
    state: index >= 2 ? 'blocked' : index === 0 && qualified ? 'qualified' : 'watching',
    reason_codes: [index >= 2 ? 'INELIGIBLE' : qualified ? 'BREAKOUT_CONFIRMED' : 'WAITING'],
    reasons: [index >= 2 ? 'Dated options eligibility is unavailable.' : qualified ? 'Completed close is above the opening range.' : 'Waiting for a post-range completed bar.'],
    last_price: 103, last_bar_end: asOf,
    opening_range_high: 102, opening_range_low: 99,
    return_pct: 3, benchmark_return_pct: 0.3, relative_return_pct: 2.7,
    eligibility: index >= 2 ? 'unknown' : 'eligible',
    fundamentals_status: index === 1 && asOf === times[2] ? 'available' : 'unknown',
    evidence: index === 1 && asOf === times[2] ? [lateEvidence] : [],
    bars: [{ bar_end: '2026-10-30T09:20:00+05:30', close: 100 }, { bar_end: asOf, close: 103 }],
    contract_status: 'not_evaluated',
  }));
  return {
    mode: 'synthetic_demo', as_of: asOf, rule_version: 'opening-range-v0.1',
    source: 'Bundled synthetic fixtures',
    summary: { total: 5, qualified: qualified ? 1 : 0, watching: qualified ? 1 : 2, blocked: 3 },
    candidates,
  };
}

export function jsonResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json' } });
}
