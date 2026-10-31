export interface DemoConfig {
  mode: 'synthetic_demo';
  label: string;
  source: string;
  replay_times: string[];
  default_as_of: string;
}

export interface Evidence {
  id: string;
  kind: string;
  title: string;
  summary: string;
  period: string;
  source: string;
  source_url: string | null;
  published_at: string;
  available_at: string;
}

export type ScreenState = 'qualified' | 'watching' | 'blocked';

export interface Candidate {
  symbol: string;
  name: string;
  sector: string;
  rank: number | null;
  state: ScreenState;
  reason_codes: string[];
  reasons: string[];
  last_price: number | null;
  last_bar_end: string | null;
  opening_range_high: number | null;
  opening_range_low: number | null;
  return_pct: number | null;
  benchmark_return_pct: number | null;
  relative_return_pct: number | null;
  eligibility: 'eligible' | 'ineligible' | 'unknown';
  fundamentals_status: 'available' | 'unknown';
  evidence: Evidence[];
  bars: { bar_end: string; close: number }[];
  contract_status: 'not_evaluated';
}

export interface Replay {
  mode: 'synthetic_demo';
  as_of: string;
  rule_version: string;
  source: string;
  summary: { total: number; qualified: number; watching: number; blocked: number };
  candidates: Candidate[];
}
