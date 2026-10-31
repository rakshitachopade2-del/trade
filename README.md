# Trade — research desk

A local research foundation for an Indian stock-options decision-support app. Built with React, TypeScript, CSS modules and Python/FastAPI.

**Current milestone: synthetic replay only.** All instruments, prices, eligibility records and quarterly evidence in the bundled demo are fictional. There is no Zerodha connection, live feed, AI inference, options P&L, order execution or demonstrated trading edge.

## Run on your computer

Requirements: Python 3.11+ and Node.js 22.22.2+, 24.15+ or 26+ (the locked test dependencies require these versions). With nvm, run `nvm install` and `nvm use` from the repository root. Run the backend commands from the repository root.

Terminal 1:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e '.[dev]'
.venv/bin/python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```

Terminal 2:

```bash
cd frontend
npm ci
npm run dev
```

Open the local URL printed by Vite (normally http://127.0.0.1:5173). The frontend forwards `/api` requests to port 8000. Keep both processes running. No API keys or AI subscriptions are needed to run this demo. If a port is occupied, stop the old project process or update both server/proxy configuration deliberately.

For the backend's recorded dependency versions, install `backend/requirements.lock` before the editable project:

```bash
.venv/bin/python -m pip install -r backend/requirements.lock
.venv/bin/python -m pip install --no-deps -e .
```

## Verify behavior

```bash
.venv/bin/python -m unittest discover -s backend/tests -v
.venv/bin/python -m backend.app.validate
npm --prefix frontend test
npm --prefix frontend run typecheck
npm --prefix frontend run build
```

With the development servers stopped, run the HTTP integration check:

```bash
.venv/bin/python scripts/check_http.py
```

It starts and stops its own servers on loopback ports 8000 and 15173 and verifies all three replay times through the real frontend proxy. It is not a visual browser check.

For rendered browser verification, install Google Chrome and stop the development servers, then run:

```bash
npm --prefix frontend run test:browser
```

Playwright uses installed Chrome and starts its own servers on ports 8000 and 15173. Eight checks cover desktop, tablet, mobile and narrow-mobile layouts, all replay times, evidence cutoffs, exclusion reasons, keyboard navigation, automated accessibility checks, and an actual backend shutdown/restart. Screenshots and failure traces stay in ignored `artifacts/browser/`. The suite stops only its own backend process and refuses an occupied backend port. This is Chromium verification, not a Safari/Firefox or physical-device certification.

In the dashboard, change the replay clock:

1. **09:30 IST:** the opening range has just completed; a later confirmation bar is still needed.
2. **09:35 IST:** the clean fictional example qualifies for the underlying screen. Other examples show waiting or exclusion reasons.
3. **09:40 IST:** a later synthetic evidence item becomes available. It must not appear at 09:35.

Select the unknown-fundamentals example: missing financial evidence stays unknown. Select excluded examples to see eligibility and stale/missing-data reasons. A qualified underlying still says its option contract has not been evaluated. Stop the backend and refresh: the UI should show an error, never replacement prices.

## What the screen computes

`opening-range-v0.1` compares the latest completed close with the high of exactly the first three five-minute session bars. It also compares stock and benchmark returns from their respective first session opens at the same bar end. Every required record must be available by the replay clock. Missing/stale data and unknown or ineligible listed-options status block qualification.

Priority is a deterministic research ordering, **not a probability of profit**. Fundamentals are a separate sourced-evidence panel in this milestone, not a bullish vote. No buy/sell action is provided.

## Bring data later

The CLI can validate a directory containing the four CSV files described in [data/README.md](data/README.md):

```bash
.venv/bin/python -m backend.app.validate /absolute/path/to/your/csv-directory
```

External directories are labelled `unverified_import`. Passing schema checks establishes structural validity only, not factual correctness, licensing, complete coverage or freedom from hindsight. The HTTP demo continues to serve bundled synthetic fixtures. Real-data display and broker adapters are the next milestone.

Keep credentials, trade exports and proprietary datasets in ignored local storage, not this public code repository. Use a local secret store when authentication is eventually added.

## Project map

- `frontend/`: React dashboard, typed API client and CSS modules.
- `backend/app/`: CSV validation, pure replay calculations and read-only HTTP API.
- `backend/tests/`: meaningful data and time-boundary regression tests.
- `data/synthetic/`: explicitly fictional input fixtures.
- `docs/PROJECT_BRIEF.md`: agreed scope and unresolved product choices.
- `docs/MILESTONE_1.md`: current behavior and acceptance criteria.
- `docs/API_CONTRACT.md`: shared response contract.
- `docs/STATUS.md`: verified progress and next work.
- `docs/LOCAL_CODEX_HANDOFF.md`: instructions for continuing in VS Code.

## Development and deployment

The repository, not any chat session, holds project state. Read `AGENTS.md` before changes. This prototype is intended for loopback development; authentication, durable storage, exchange calendar support, worker supervision, live feed permissions, backups and deployment hardening are not implemented. Do not expose its development servers publicly.

The next useful experiment is a small real-data coverage trial and sourced quarterly evidence, followed by frozen numerical rules and honest evaluation. A live options strategy needs actual contract identity, executable quotes, costs, human delay and prospective validation; underlying candles alone are insufficient.
