# Trade research workspace

Build a private Indian stock-options research assistant. The user makes every trade manually in the broker terminal. No order creation, cancellation, GTT, auto execution, or broker credentials in frontend code.

## Development
- Read `docs/PROJECT_BRIEF.md`, `docs/MILESTONE_1.md`, `docs/API_CONTRACT.md`, and `docs/STATUS.md` before substantive work.
- React + TypeScript with separate CSS modules. No Framer Motion. Python + FastAPI for the API; keep calculations in dependency-light pure functions.
- Preserve user work. Inspect status before edits. Do not change global Git identity, force-push, rewrite history, or publish secrets/data.
- Use small, reviewable changes. Record actual commands/results and limitations in `docs/STATUS.md`. Never claim unrun checks passed.
- No paid APIs, deployment, scheduled cloud work, or account connections without the user's corresponding instruction.

## Research integrity
- Synthetic fixtures must remain prominently labelled. No generated price or financial value may be presented as real market evidence.
- Only information available at the chosen as-of timestamp may affect a calculation. Completed candles require their end time and availability time to be at or before as-of.
- The universe is stocks with dated listed-options eligibility; Nifty and sectors are context. Eligibility is not contract liquidity.
- Missing financials stay unknown. Good results and low valuation do not establish downside protection for a call option.
- No probability of profit, win-rate claim, or options P&L without the corresponding empirical/contract evidence.
- Source identity, timestamps and rule versions travel with computed results. No model call is needed for the first milestone.
