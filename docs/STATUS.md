# Project status

Updated: 31 October 2026 (IST).

## Repository inspection

- The downloaded project lives in `Trade_Milestone_1_Starter/trade/`; neither it nor the outer folder initially contained Git metadata.
- `git ls-remote --symref https://github.com/rakshitachopade2-del/trade.git` succeeded and returned no refs, both before setup and after verification. No remote history existed to merge.
- Initialized `main` in the existing `trade/` directory and set `origin` to that URL, preserving all supplied application files. No global Git identity changes or history rewrites.
- This is now the user's local macOS working copy, replacing the earlier cloud-workspace handoff state.
- No broker, paid API, AI inference provider, production deployment or schedule is connected.

## GitHub synchronization

- Verified application committed locally as `d7e5179` (`Complete synthetic replay milestone and browser verification`).
- The first push returned HTTP 403 for the configured account `RakshitChopade26`. The user subsequently granted collaborator access.
- On 31 October 2026, `git push -u origin main` succeeded using the existing authentication, publishing `d7e5179` and the handoff update `dd5785d`. Local `main` now tracks `origin/main`; the authentication blocker is resolved. Global Git identity was not changed.
- The local frontend and backend were started successfully; the frontend returned HTTP 200 and `/api/health` returned `synthetic_demo` with `orders_enabled: false`.

## Current milestone

Milestone 1: synthetic research replay foundation implemented and locally verified. React/TypeScript dashboard, CSS modules, FastAPI read-only endpoints, strict CSV validator, deterministic as-of engine, five fictional underlyings and one benchmark, evidence availability, and documented local setup.

At 09:30 the fixture returns 0 qualified / 2 watching / 3 blocked. At 09:35 and 09:40 it returns 1 qualified / 1 watching / 3 blocked. BETA's synthetic quarterly evidence is unknown at 09:35 and available at 09:40; moving back removes it. DELTA has unknown eligibility, GAMMA is ineligible, and EPSILON has stale/incomplete bars. Eligibility does not imply contract suitability; all contracts remain unevaluated.

## Local setup and fixes

- Default system Python was 3.9.6, below the required 3.11. Installed uv temporarily with `python3 -m pip install --target /private/tmp/trade-bootstrap uv`, then installed Python locally with `/private/tmp/trade-bootstrap/bin/uv python install 3.12 --install-dir .python --no-bin --cache-dir /private/tmp/trade-uv-cache`.
- Created `.venv` with `.python/cpython-3.12.16-macos-aarch64-none/bin/python3 -m venv .venv`. Installed `.venv/bin/python -m pip install -r backend/requirements.lock` and `.venv/bin/python -m pip install --no-deps -e .` successfully. Keep `.python/`: this virtual environment uses that interpreter.
- Selected already-installed Node 24.21.0 using `source /opt/homebrew/opt/nvm/nvm.sh` and `nvm use 24.21.0`; `npm ci` succeeded. Default Node 24.13.0 caused engine warnings. Updated `.nvmrc`, README and package engines to match supported runtimes.
- Added Playwright, axe and Node type declarations as development dependencies with `npm install --save-dev @playwright/test @axe-core/playwright` and `npm install --save-dev @types/node@24`. Lockfile updated; npm reported zero vulnerabilities.
- Browser checks exposed insufficient sidebar/selected-row text contrast and a replay label hidden from accessibility tools below 360px. Increased contrast and kept the narrow-screen label accessible using visually hidden CSS.
- Added a repeatable browser suite, included its TypeScript in typecheck, and ignored local Python runtimes and browser artifacts. Initial browser failures and a missing Node-types error were corrected before the final passing runs.
- Sandbox DNS/server restrictions blocked initial install and HTTP/browser attempts. Authorized reruns with network/loopback access succeeded; these infrastructure failures are not counted as passing checks.

## Validation

Final successful commands from the repository root (frontend commands use Node 24.21.0):

- `.venv/bin/python -m unittest discover -s backend/tests -v`: **25 passed**.
- `.venv/bin/python -m backend.app.validate`: valid bundled fixtures; **6 instruments, 27 bars, 5 eligibility records, 2 evidence records**.
- `.venv/bin/python -m pip check`: no broken requirements.
- `npm --prefix frontend test`: **6 Vitest/jsdom tests passed**.
- `npm --prefix frontend run typecheck`: passed, including browser test/config files.
- `npm --prefix frontend run build`: passed; **44 modules**, production assets generated in ignored `frontend/dist/`.
- `npm --prefix frontend run test:browser`: **8 passed** in 25 seconds with installed Google Chrome. Desktop 1440×1000, tablet 768×1024, mobile 390×844 and narrow mobile 320×740.
- `.venv/bin/python scripts/check_http.py`: passed all three replay times through the actual Vite proxy and FastAPI, including `orders_enabled: false`.

Browser verification covers replay counts, no post-range confirmation at 09:30, ALPHA qualification at 09:35, BETA evidence appearing at 09:40 and disappearing on rewind, unknown financials, all three exclusion types, unevaluated contracts, keyboard skip navigation and candidate selection. The suite actually stops its own backend, verifies refresh and page reload clear results, then restarts it and verifies Retry connection recovers. Expected proxy connection errors occur during that outage test.

Axe WCAG A/AA automated checks reported zero violations in the checked ALPHA, unknown-financials BETA and offline states at all four widths. Horizontal overflow checks passed. Rendered screenshots for desktop, tablet, mobile and narrow layouts plus the mobile offline state were visually inspected: panels, controls, charts and evidence remained intact without clipping or overlap. Screenshots are retained locally in `artifacts/browser/`, excluded from Git.

Test environment: macOS arm64, Python **3.12.16**, Node **24.21.0**, npm **11.19.0**, Chrome **156.0.8078.80**, Playwright **1.64.1**, axe **4.14.0**, React **19.3.1**, Vite **7.3.7**. Starlette still emits its non-failing httpx TestClient deprecation warning.

The previously outstanding visual browser verification is complete for Chrome and emulated viewports. Safari, Firefox, physical mobile devices and a full assistive-technology audit were not tested. No real market dataset, historical trading-performance study, broker connection, AI integration, production deployment or profitable strategy has been validated.

## Local app

Start the backend from `trade/` with `.venv/bin/python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000`. In another terminal, run `nvm use` from `trade/`, then `npm --prefix frontend run dev -- --port 5173 --strictPort`.

Open **http://127.0.0.1:5173**. Both development processes must remain running. Stop them before running the HTTP or browser suites, which own ports 8000 and 15173.

## Next milestone

The next smallest experiment is a small licensed real-data coverage trial: dated stock-options eligibility and a few underlyings' candles, plus one sourced quarterly filing with publication/availability timestamps. Verify fields, coverage and permissions before purchasing access or adding a broker adapter. This work remains deferred pending the user's instruction.
