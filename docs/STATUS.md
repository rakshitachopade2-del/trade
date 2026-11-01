# Project status

Updated: 1 November 2026 (IST).

## Milestone 2A — local implementation, 1 November 2026

**M2A software implemented; real-data coverage experiment pending input.** No genuine candle export, stock list, exchange listing document or quarterly filing was supplied. All exercised complete-path data and documentary review records are clearly labelled invented software fixtures.

- Started from clean `main` at `a407e043e781d4d5e88794173f046c5d04ba6477`; remote main matched. No additional AGENTS.md files applied. Work is on `feat/milestone-2a-local-intake`, for local review only. No M2A push or deployment was performed; the earlier GitHub synchronization section below describes M1 history.
- Added a bounded offline `python -m backend.app.intake` CLI: explicit manifest schema, normalized text/CSV stock lists, three-equity/one-index candle coverage, file hashes, actual ingestion timestamps, immutable run directories, and separately attributed earlier-acquisition claims. No historical `available_at` is invented.
- Added manual filing intake with source-document hashes, exact/date-only/unknown publication precision, separately recorded transcription/reconciliation, nullable figures and guarded YoY comparisons. No OCR, LLM extraction or financial score.
- Kept user membership assertions separate from dated documentary review, and listing separate from ban/liquidity. Unknown mappings and missing/zero equity/index volume remain distinct. Conflicting duplicates invalidate coverage; no prices are filled.
- Added a sanitized read-only `/api/data-coverage` route controlled only by backend `TRADE_COVERAGE_REPORT`, with no HTTP upload/path selection/raw-file/URL-fetch endpoints. Missing configuration, malformed report, invalid inputs, partial/complete coverage and backend failure remain distinct.
- Added the collapsible Data coverage component and CSS module below the existing research desk. Dataset nature stays visible even when collapsed. Research labels, M1 fixtures/calculations and unevaluated contract statuses remain unchanged.
- Added clearly synthetic examples, blank user-input templates and `docs/MILESTONE_2A.md`; updated README, data documentation and API contract. Used existing Python/Node environments and dependencies; no environment rebuild or package installation was needed.
- Original development backend PID 76525 was verified by command and working directory before stopping it for port-owning checks. The existing frontend process on 5173 belongs to this project. No unrelated process was stopped.

### M2A verification actually run

Python **3.12.16**, Node **24.21.0** via `source /opt/homebrew/opt/nvm/nvm.sh` and `nvm use 24.21.0`; existing Chrome **156.0.8078.80**.

| Command (repository root) | Actual result |
| --- | --- |
| `.venv/bin/python -m unittest discover -s backend/tests -v` | **45 passed**: original 25 plus 20 intake/API/CLI boundary tests. |
| `.venv/bin/python -m backend.app.validate` | Passed: original 6 instruments / 27 bars / 5 eligibility / 2 evidence records. |
| `.venv/bin/python -m backend.app.intake data/intake-example` | Exit **0**, explicitly **synthetic_test**; 9 unique intervals per series / 36 total, one 10:00-start row outside coverage, one list duplicate removed. |
| `.venv/bin/python -m backend.app.intake data/intake-template` | Expected exit **1**, partial; zero price bars, unknown membership, filing not imported, retention unresolved. Provider bytes not retained. |
| CLI ready/partial/malformed boundary checks in `test_intake.py` | Verified exit **0/1/2**, respectively, plus rejection of output outside ignored private-data. |
| `npm --prefix frontend test` | **12 passed**, including M1 regression and coverage state/validation tests. |
| `npm --prefix frontend run typecheck` | Passed, including browser test/config files. |
| `npm --prefix frontend run build` | Passed; **47 modules**. |
| `.venv/bin/python scripts/check_http.py` | Passed all three M1 replay times through the real Vite proxy, disabled orders, and no-import coverage route with an ignored caller-supplied path. |
| `npm --prefix frontend run test:browser` | **12 passed** in 44.0 seconds; actual importer + API, desktop/tablet/mobile/320px narrow viewports. |
| `git diff --check` | Passed. |

Browser coverage includes original replay/evidence/exclusion checks, independent coverage refresh, complete-synthetic/partial/invalid-input/incompatible-report/not-imported states, actual backend stop/restart, keyboard expansion/refresh and unchanged synthetic research. Axe checks reported no violations in the checked states; document-width checks passed. Desktop complete and narrow-mobile partial/complete screenshots were inspected with no clipping or overlap; long identifiers wrap on narrow screens. Artifacts remain ignored. Tests mutate only a separate disposable report copy, preserving the original import run.

One initial schema-import smoke check exposed an annotation typo while authoring the new code; it was corrected before the passing suites. Review also tightened blank-review/source-symbol rejection, report-version/consistency validation and preservation of full manifest metadata in normalized provenance. The existing Starlette/httpx deprecation and expected Vite proxy errors during deliberately induced outages are non-failing.

No required software check remains unrun. Safari/Firefox, physical devices, a full assistive-technology audit and genuine provider/data coverage were not tested. The app remains a loopback prototype without authentication or production hardening. No broker, paid API, source scraping, external data acquisition, AI calls or cloud jobs were added.

### Owner input needed next

Provide a stock list with optional source/date; one export permitted for local retention covering the selected three equities and Nifty spot for a confirmed session (nine five-minute intervals each); and one permitted filing document plus manually sourced metadata/page references. Exact dissemination support and dated stock-option evidence can be supplied later, but their coverage checks stay partial until then. No credentials are requested. See `docs/MILESTONE_2A.md` for the exact schemas and commands.

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

## Milestone 1 history

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

## Milestone 1 validation history (31 October 2026)

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

## Next data experiment

M2A offline software is ready for the specific owner inputs listed above. A genuine coverage result remains pending those inputs and manual reviews. Broker/API integration, paid access and any trading-performance experiment remain outside this implementation.
