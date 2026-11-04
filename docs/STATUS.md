# Project status

Updated: 4 November 2026 (IST).

## Owner-confirmed dated eligibility — 4 November 2026

- The owner explicitly confirmed the three displayed matches: "Yeah, I confirm that they are correct." Recorded this as manual confirmation of the INFY, RELIANCE and HDFCBANK stock-option evidence for 30 October 2026 only. No adjustment, source/session, filing, liquidity or ban-status review was inferred.
- Prepared fresh ignored bundle `private-data/kite-eligibility-confirmed-20261104T124020712870Z/`, copying the prior candle/list inputs and checked NSE CSV. New manifest evidence entries have `review.confirmed: true` and an attributed reference to the owner's confirmation and original review packet. `owner-confirmation.json` preserves the exact message, recording time, reviewed rows, document hashes and scope. Original pending review packet and prior input/report bytes remain unchanged; 26 prior files verified by SHA-256 and mtime.
- Ran `.venv/bin/python -m backend.app.intake private-data/kite-eligibility-confirmed-20261104T124020712870Z/input --output-root private-data/kite-eligibility-confirmed-20261104T124020712870Z/imports` (absolute paths in execution). **Exit 1, partial**. All four instruments retain **9/9 bars, 36/36 total**; normalized bars including NIFTY50 volume zeroes match the prior import exactly. All three equities now have supporting evidence and dated manual review confirmed. `eligibility_review_pending` is cleared.
- Remaining gaps exactly: `adjustment_unknown`, `filing_missing`, `session_review_pending`, `source_review_pending`. Source/session flags remain false; adjustment unknown; filing absent. Actual ingestion: `2026-11-04T12:40:21.809148Z` (**18:10:21.809148 IST**, 4 November 2026).
- New report: `private-data/kite-eligibility-confirmed-20261104T124020712870Z/imports/20261104T124021809148Z-4c49bd8c9e95/report.json`. Restarted only the verified Trade backend to select this report (new PID 63237); frontend remains on `http://127.0.0.1:5173/#data-coverage`. Chrome/API verification passed: three manually confirmed membership rows, partial state, four 9/9 rows, saved-report equality and unchanged synthetic research. New private bundle contains restart instructions, screenshot, verification JSON and receipts.
- The confirmation/import step made no application-source changes, network data acquisition, full-suite rerun, broker connection, commit, push, deployment or trade. The owner subsequently requested an AI handoff under the standing instruction to publish status first; only this status document is included. Private market inputs, review packets and reports remain excluded. Prior entries below describe the earlier pending stages.

Next bounded task: verify the original filing referenced by the existing local source pack and prepare its evidence for review. The candle import and eligibility confirmation are complete; no software rebuild is indicated. Filing publication precision and reconciliation must remain unknown/pending wherever supporting information is absent. Adjustment and source/session review are separate remaining gaps.

## Three-row NSE eligibility review prepared — 4 November 2026

- At the owner's request, downloaded the official 30 October 2026 F&O-UDiFF Common Bhavcopy Final from `https://nsearchives.nseindia.com/content/fo/BhavCopy_NSE_FO_0_0_0_20261030_F_0000.csv.zip`. Actual acquisition: `2026-11-04T11:53:56.935580+00:00`; no historical application availability inferred. Initial sandbox DNS failure was resolved by approved access to this exact public source.
- Downloaded ZIP is 1,066,684 bytes and exactly matches the existing source pack's expected SHA-256 `99da5162c5e18aa4f79183a0c546780d07d5c1dedfbbcb5f1a0fbf55af28158b`. Its sole CSV member is `BhavCopy_NSE_FO_0_0_0_20261030_F_0000.csv`, 6,168,700 bytes, SHA-256 `032c95541aa0dcef0770818b87d5d33d415da5010a13410dc243dc466781c706`.
- Matched exactly one stock-option contract each for INFY, RELIANCE and HDFCBANK against the source pack, checking trade/business date, NSE/FO/STO identifiers, symbol, contract ID/name, CE/PE, both expiry fields, strike, reported total trading volume and exact physical CSV line. Row locators include the header as line 1. The separate contract master was not re-downloaded or revalidated in this task.
- Ignored private review packet: `private-data/eligibility-review-20261030-20261104T115356935998Z/`. Includes original ZIP, exact extracted CSV, acquisition receipt, `review-rows.csv`, `eligibility-review.json`, `REVIEW.md` and schema-validated `eligibility-evidence-pending.json` pointing to the extracted CSV's hash. All three `review.confirmed` flags remain **false** and references **null**, awaiting owner review.
- Source-pack bytes unchanged. Existing import inputs/reports and Data coverage configuration were not changed or rerun; eligibility remains pending there. This is retrospective contract evidence for the stated date, not proof of pre-open knowledge, next-session listing, ban status, liquidity or trading suitability. No application-code changes, full test rerun, broker connection, commit, push or deployment.

## Owner-authorized Kite ChartIQ local import — 4 November 2026

- The owner explicitly authorized importing the four exports and retaining originals/normalized copies on this Mac for private offline research. The fresh input manifest sets `retention: permitted`; its note records authorization dated **4 November 2026** and **provider permission was not independently verified**. This supersedes the earlier owner-authorization blocker below; it does not establish provider permission.
- Kept branch/HEAD `feat/milestone-2a-local-intake` / `b7839d9` and the optional-figures correction unchanged. Original Downloads exports, existing private samples/reports and the public-source pack were preserved. No application-source changes or new dependencies.
- Fresh ignored bundle: `private-data/kite-chartiq-20261030-20261104T110254383974Z/`. `raw-exports/` retains byte-identical originals, `input/` contains the prepared M2A files, and `conversion-receipt.json` records hashes, original row numbers, original timestamp/volume text, mapping basis and transformations. The existing supplied stock list was copied as an unverified user assertion; all dated eligibility reviews remain false. No filing was imported.
- Used INFY `(1).csv` with Volume plus RELIANCE/HDFCBANK/NIFTY 50 exports from `Downloads/re (1)/`. User instrument identification matches filenames; CSVs have no instrument column. NIFTY 50 is explicitly mapped to `NIFTY50` spot index. Date strings explicitly contain GMT+0530; selected starts are 09:15 through 09:55, excluding 10:00. Candle-start interpretation follows the requested opening sample and export session starts at 09:15, with no independent provider specification claimed; source/session reviews remain pending. Equity volume thousands separators were removed for integer parsing, with raw text retained in the conversion receipt. All nine index volume zeroes remain `0` / `provider_zero`, not missing or inferred trading volume.
- Actual CLI: `.venv/bin/python -m backend.app.intake private-data/kite-chartiq-20261030-20261104T110254383974Z/input --output-root private-data/kite-chartiq-20261030-20261104T110254383974Z/imports` (executed with absolute paths). **Exit 1**, **partial**, **user_import**; accepted **INFY 9/9, RELIANCE 9/9, HDFCBANK 9/9, NIFTY50 9/9**, total **36/36**. No invalid-row diagnostics. All normalized OHLCV values were checked against the selected original rows.
- Actual ingestion: **2026-11-04T11:03:13.400608Z**, or **4 November 2026, 16:33:13.400608 IST**. The historical sample/as-of date is 30 October 2026; no earlier acquisition or historical availability time was invented.
- Report: `private-data/kite-chartiq-20261030-20261104T110254383974Z/imports/20261104T110313400608Z-4ec8a7f608b0/report.json`. Remaining gaps exactly: `adjustment_unknown`, `eligibility_review_pending`, `filing_missing`, `session_review_pending`, `source_review_pending`. Adjustment stays unknown; source/session reviews pending; filing values/publication/reconciliation unknown; eligibility unverified. Complete bar coverage does not mean overall coverage or genuine source verification succeeded.
- Started loopback backend on port 8000 with `TRADE_COVERAGE_REPORT` pointing to that report, and frontend on 5173. The sandbox initially denied port binding; approved local-server launches succeeded. Live URL: `http://127.0.0.1:5173/#data-coverage`. Chrome verified the panel shows Partial, User import and four 9/9 rows; the API projection equals the saved report. Synthetic research labels and unevaluated contracts remain intact. Screenshot and verification JSON are in the private bundle, with restart instructions in its `README.txt`.
- Verified Git ignores the fresh private bundle. Existing importer plus targeted row/provenance/API/browser checks were used; unchanged-code unit suites/build were not rerun. During import preparation only local/offline file processing and loopback requests occurred; no commit or push was made then. The owner subsequently authorized committing and pushing this status update for the coordinating AI. Private exports, inputs, reports and reference-pack files are excluded from publication. No broker connection, purchase, external data acquisition, deployment or trading.

## Kite ChartIQ import permission check — 4 November 2026

- Preserved `feat/milestone-2a-local-intake` at `b7839d9e4fa35414e89d392bdb1660a46fe775ba`. The optional-figures correction is already committed; no uncommitted tracked changes existed at task start. The untracked public-source pack remains untouched.
- Located the requested INFY `(1).csv` by filename in `~/Downloads`; RELIANCE, HDFCBANK and NIFTY 50 CSVs are in `~/Downloads/re (1)/`. Only filenames were inspected: provider CSV contents were not opened, hashed, copied or transformed. All exports remain in their original locations.
- No documented Kite/ChartIQ basis permitting this private local import and retention was found in the local project/reference records or alongside the located exports. `private-data/real-sample/manifest.json` still has `retention: unresolved` and no retention note. The public-source pack explicitly leaves permitted use unresolved and supplies no Kite-specific permission. Export availability alone was not treated as permission. No online terms check was made, following the offline-only instruction; this is an unresolved evidence gap, not a determination that the use is prohibited.
- Importer **not run**: CLI exit code **not applicable**, no new report or ingestion timestamp, accepted bars per instrument **not assessed** (not zero). No new private input directory was prepared. Target remains 30 October 2026, 09:15–10:00 IST, nine five-minute bars per instrument, 36 total. Mappings, timestamp convention, interval coverage, INFY Volume column and reported index zeroes await inspection after permission is established. Adjustment, filing evidence and required reviews remain unknown/pending.
- No application code, private inputs, immutable reports or confirmations changed. Tests/build were not rerun for this documentation-only permission check. No network/broker connection, purchase, commit, push, deployment or trading occurred.

Earlier question for Zerodha support (historical reference; no further response is required to complete the owner-authorized import above):

> May I import CSV files manually exported from Kite's ChartIQ charts into a private offline application on my own computer and retain both the original CSVs and normalized copies for my own non-commercial research? The sample is NSE cash-market INFY, RELIANCE and HDFCBANK plus NIFTY 50 spot, using five-minute OHLC/volume bars for 30 October 2026, 09:15–10:00 IST (nine bars per instrument). There will be no redistribution, public display, cloud upload, automated downloads, API/broker connection or order placement. Please identify the applicable Zerodha, ChartIQ/data-provider and exchange terms or written permission covering this use, including any retention/deletion limits and whether separate permission is required for NIFTY 50 index data.

## Optional financial figures correction — 1 November 2026

- Corrected on existing `feat/milestone-2a-local-intake`, starting at reviewed HEAD `4b9ddea8e949814696ac39e4efdbbf60eaf45725`. No newer tracked changes were present. The correction was initially left uncommitted for review; the owner subsequently authorized commit and push to this feature branch. No reset or branch change. The supplied untracked `Dev Ref/Trade_Public_Data_2026-11-01/` was preserved.
- New imports no longer emit `filing_figures_missing` solely for absent optional figures. `figures_present` remains an accurate integer 0–3; backend and frontend accept zero in otherwise complete reports. UI explicitly says absent financial values remain unknown. Figure schema, YoY rules, filing document/source/publication support/reconciliation reference and all other required coverage checks are unchanged; reconciliation is never assigned automatically.
- Older immutable reports retain their original status and legacy gap code, with UI guidance to rerun original permitted inputs into a new run and configure its report path. No existing report was migrated. Current contract and rerun instructions are in `docs/API_CONTRACT.md` and `docs/MILESTONE_2A.md`. This resolves the figure-gate finding in the historical entries below.
- Regressions cover omitted fields, explicit null fields and a valid figure object with null current value; all three pass complete intake/CLI/API with zero figures, preserving unknown values/YoY. Other tests cover malformed/nonfinite supplied figures, invalid counts, missing filing/document/publication support/source/reconciliation/reference, pending source/session/eligibility reviews, missing candles and legacy reports.

### Verification actually run for this correction

| Command/check | Actual result |
| --- | --- |
| `.venv/bin/python -m unittest backend.tests.test_intake -v` | **25 passed** in 3.430 s, including five new regression methods and their subcases. Exercises CLI and coverage API. |
| `npm --prefix frontend test` | **17 passed** across both frontend test files, including five new coverage tests. |
| `npm --prefix frontend run typecheck` | Passed. |
| `npm --prefix frontend run build` | Passed; 47 modules. |
| `npm --prefix frontend run test:browser -- --grep 'coverage view|optional financial figures' --output artifacts/optional-figures-20261101T181533/browser` | **8 passed** in 34.3 s: real importer/API, zero-figure complete state, legacy partial state and existing coverage states across desktop/tablet/mobile/320px. |
| Accessibility/layout and screenshots | Checked browser states had no axe violations or horizontal overflow. Desktop and 320px zero-figure screenshots visually inspected; optional/unknown explanation visible without clipping. |
| Preservation inventory | **119 existing files unchanged** by SHA-256, byte length and mtime: private inputs/import reports and the supplied reference pack. New browser imports use invented fixtures in new run directories. |
| `git diff --check` | Passed. |

Used existing Python 3.12.16 and Node 24.21.0 environments; no dependencies installed. Existing Starlette/httpx and Playwright color-environment warnings are non-failing. Expected proxy errors during the coverage outage/recovery check are recorded. The verified project backend on port 8000 was temporarily stopped for browser checks and restored (PID 56191) with its original `not_imported` coverage state. Logs/screenshots and preservation checks are in ignored `artifacts/optional-figures-20261101T181533/`.

Not rerun: full backend discovery, standalone M1 replay/outage browser tests, fixture-validation/HTTP helper checks, Safari/Firefox or physical-device checks. The affected intake suite, full frontend unit suite and coverage browser regressions above passed; no genuine-data intake was performed for this correction.

### Supplied public-source pack inspection (read-only)

Read `Dev Ref/Trade_Public_Data_2026-11-01/READ_ME_AND_CODEX.txt` and inspected its six-file pack. It contains a three-symbol list, example option rows, source manifest, eligibility-review drafts and transcribed filing metadata; original provider documents and candles are absent. Draft eligibility reviews remain false, filing publication is date-only and transcription is not reconciled. The pack itself states that retention permission and real-data coverage are not established. Its source/figure claims were not independently verified against originals in this task.

The existing `private-data/real-sample/` still has its original blank/scaffolding inputs and unresolved retention. No pack files were copied into it, no inputs/review confirmations were changed, and no URLs were fetched, following the current instruction to correct only software and avoid acquisition/private-input changes. The pack remains untracked and is not included in any commit. Genuine validation still needs permitted candle inputs, matching original supporting documents, exact dissemination support and required source/session/eligibility/reconciliation reviews; optional financial figures are no longer a blocker. No broker/API connection, purchase, deployment or trading occurred.

## Owner-authorized feature-branch publication — 1 November 2026

- Following explicit owner instruction to commit and push, `git push -u origin feat/milestone-2a-local-intake` published implementation `9f0a1d04a534d741130217b74d8cc25c856d95b4`. `git ls-remote` confirmed the exact branch commit; remote main remains `a407e043e781d4d5e88794173f046c5d04ba6477`.
- The accompanying documentation update records review findings and adds `Dev Ref/M2A_REVIEW_PREPARATION.md` and `Dev Ref/M2A_AI_CHAT_HANDOFF.md`. Read the shorter preparation handoff first. Ignored review artifacts and private sample inputs/reports remain local-only.
- At that publication stage no application behavior changed. The financial-figure gate remained unresolved and genuine-data validation remains pending (exit 1, partial, 0/36 bars). Existing implementation test results below are historical; full suites were not rerun for this documentation-only update.
- No merge, history rewrite, global Git identity change or deployment. Earlier local-only/no-push entries describe their respective stages and are superseded by this publication update.

## Bounded M2A review preparation — 1 November 2026

- Preserved `feat/milestone-2a-local-intake` at `9f0a1d04a534d741130217b74d8cc25c856d95b4`. Exported 36 committed files/additions/tests against `a407e043e781d4d5e88794173f046c5d04ba6477` to ignored `artifacts/reviews/m2a-9f0a1d0/M2A_committed_review.patch`. Credential-pattern and data-inventory checks found no credentials/private market inputs; exported data is synthetic fixtures or empty templates.
- Initial state: no tracked edits; only `Dev Ref/M2A_AI_CHAT_HANDOFF.md` untracked. This task adds this documentation log and `Dev Ref/M2A_REVIEW_PREPARATION.md`, excluded from the committed patch. No commits/pushes/resets during that bounded preparation.
- Historical finding (subsequently corrected above): null figures are schema-valid (`schema.py:192`), but zero current figures adds `filing_figures_missing` (`runner.py:335`) and gates overall completion (`runner.py:346`, `report.py:134`, frontend coverage validator `:90`). Isolated synthetic probe: otherwise complete, 36 bars, exact/reconciled filing, all figures null => partial with that sole gap. Two related existing tests passed; no full-suite rerun.
- Created ignored `private-data/real-sample/` from the blank template because it was absent. Candidate mappings preserved, user_import, empty list/header-only candles, no configured filing, null figures/unknown publication, unresolved retention, false reviews. Provider timezone set to null in this private copy. No invented evidence copied there; input hashes unchanged after intake.
- `.venv/bin/python -m backend.app.intake private-data/real-sample` returned exit **1**, **partial**, **0/36 bars**. Report: `private-data/imports/20261101T120739858148Z-3d1ed43fb95b/report.json`. Gaps: `adjustment_unknown`, `eligibility_review_pending`, `filing_missing`, `missing_bars`, `retention_pending`, `session_review_pending`, `source_dates_unknown`, `source_review_pending`, `source_unknown`, `stock_list_missing`. Genuine validation remains pending; provider data not read/retained while permission is unresolved.
- Short handoff and missing-files/facts checklist: `Dev Ref/M2A_REVIEW_PREPARATION.md`. Export metadata, isolated reproduction and CLI output: ignored `artifacts/reviews/m2a-9f0a1d0/`. Application source/dashboard unchanged.

## Milestone 2A — local implementation, 1 November 2026

**M2A software implemented; real-data coverage experiment pending input.** No genuine candle export, stock list, exchange listing document or quarterly filing was supplied. All exercised complete-path data and documentary review records are clearly labelled invented software fixtures.

- Started from clean `main` at `a407e043e781d4d5e88794173f046c5d04ba6477`; remote main matched. No additional AGENTS.md files applied. Implementation was prepared on `feat/milestone-2a-local-intake` for local review only. At that stage no M2A push or deployment was performed; the earlier GitHub synchronization section below describes M1 history.
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
