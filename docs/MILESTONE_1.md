# Milestone 1 — reproducible research replay

Goal: run a private local dashboard with a small deterministic dataset and prove that no future evidence enters a screen. This milestone does not test a trading edge, perform a historical market backtest, calculate options returns, or establish current F&O eligibility.

## Deliverable

React/TypeScript dashboard, Python/FastAPI API, pure calculation module, CSV fixtures/validator, meaningful automated checks, and local setup instructions. Five fictional stock underlyings plus a fictional benchmark. Every UI state and API response identifies the data as synthetic. The default API never silently falls back from a real provider to demo values.

## Screening rule: opening-range-v0.1

The first three completed five-minute bars, starting at 09:15 IST and ending at 09:30, define the session's opening range. All three must be available by as-of. Screening requires known options eligibility effective at the chosen time, completed current-session bars, no required gaps, and latest available bars no older than 300 seconds. Check benchmark completeness and freshness too.

At or after the first post-range completed bar, a stock qualifies only if its latest close exceeds the opening-range high and its return from the first session open exceeds the benchmark's return from its own session open. Relative return is the difference in percentage points. Qualifiers sort by relative return descending, then symbol ascending for deterministic ties. Other stocks remain watching or blocked with explicit reasons; blocked stocks have no priority rank. This is an illustrative screen, not an entry/stop/exit strategy.

The demo uses 09:30, 09:35 and 09:40 IST replay stops. At 09:30 there is no eligible post-range bar. At 09:35 one clean example should qualify while missing eligibility, stale data and ineligible examples remain blocked. At 09:40 a previously unavailable evidence item should appear. Missing evidence must not silently become favorable evidence. Fundamental evidence is shown separately and does not influence this initial price-screen rank.

## Acceptance criteria

- Same dataset, as-of and rule version produce identical output and ordering.
- Every calculation reads only bars with bar_end <= as_of AND available_at <= as_of; naive timestamps are rejected.
- A future candle/evidence/eligibility row cannot alter earlier output. Future extreme values are a regression test.
- Dated known eligibility is required. Unknown or explicitly ineligible stocks remain visible as excluded examples, never ranked candidates.
- Missing, malformed, nonfinite or inconsistent price data is rejected with file/row context. No silent financial-data repair.
- Conflicting duplicate identities fail validation. Invalid evidence time ordering and overlapping contradictory eligibility intervals are handled explicitly.
- Required missing bars and stale stock/benchmark data block screening. Time beyond the sample session cannot masquerade as current data.
- Quarterly evidence displays its source, period, publication time, usable time and synthetic status; absent evidence reads unknown.
- API errors appear in the UI with a retry path. Changing replay time cannot leave a previous result labelled with the new time; late requests cannot overwrite newer results.
- Frontend build/typecheck, Python calculation/API tests, and a manual/browser walkthrough are recorded honestly.
- No broker endpoints, model requests, auto orders, implied win probabilities, option lot sizing or fabricated option P&L.

## Deferred work

Real-data adapters, HTTP imports, accounts, persistent database, WebSocket collector, holiday-aware scheduler, actual earnings ingestion, AI/MCP integration, options contract analysis, backtest fill/cost engine, predictive ranking and deployment. The CSV validator is a data-quality entry point; imported real data will require a distinct provenance mode before being exposed in the dashboard.
