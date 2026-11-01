# Trade — Milestone 2A status handoff for the coordinating AI

Prepared: 1 November 2026 (Asia/Kolkata).

## Publication and review update — 1 November 2026

The owner subsequently authorized commit and push. Implementation commit `9f0a1d04a534d741130217b74d8cc25c856d95b4` is now published on [the feature branch](https://github.com/rakshitachopade2-del/trade/tree/feat/milestone-2a-local-intake). Main remains at the M1 baseline; no merge or deployment occurred.

Read [M2A_REVIEW_PREPARATION.md](M2A_REVIEW_PREPARATION.md) first for the latest findings: missing optional financial figures currently gate overall coverage completion. Behavior is unchanged. The prepared genuine-input directory returned exit 1, partial, 0/36 bars; genuine-data validation remains pending. Links to ignored artifacts and private-data are local-only and are not published in Git.

## Message from the owner

Please use this handoff to update your understanding of the project's progress and decide the next smallest useful step. M2A implementation has already been completed locally; do not send another prompt to rebuild it. Separate software acceptance from the still-pending genuine-data experiment.

Review the implemented scope and declared limitations below. Identify any concrete mismatch with your previous M2A handoff, then give me a short, prioritized next-action checklist. If a code-level conclusion needs source inspection, request the relevant local files or feature-branch diff rather than assuming the GitHub main branch contains these changes.

Do not authorize a broker connection, paid service, AI API, scraping, trading, deployment, push, or cloud schedule on my behalf. No credentials should be requested in chat.

## Current conclusion

**M2A software implemented; real-data coverage experiment pending input.**

No genuine stock list, market candle export, exchange listing evidence or quarterly filing was supplied or validated. All complete-path inputs, prices, financial figures and documentary review records used in software verification were explicitly invented fixtures.

Milestone 1 remains operational: the dashboard shows its original fictional underlyings and evidence. Imported material is not used in research rankings, existing eligibility records or fictional company cards. All option contracts remain `not_evaluated`.

## Repository and delivery state

- Repository: https://github.com/rakshitachopade2-del/trade
- Local checkout: `/Users/rakshitchopade/Downloads/Trade_Milestone_1_Starter/trade`
- M2A branch: `feat/milestone-2a-local-intake`
- M2A implementation commit: `9f0a1d0` — `Add offline sample intake and separate data coverage panel`
- Base/main commit: `a407e043e781d4d5e88794173f046c5d04ba6477`
- **M2A is pushed to the feature branch, with owner authorization.** It has not been merged or deployed. GitHub main still contains M1.
- Application working tree was clean at handoff preparation. This reference document was created afterward and is not part of commit `9f0a1d0`.
- Global Git identity was not changed. No environments were rebuilt or dependencies added for M2A.
- Local view: `http://127.0.0.1:5173/#data-coverage` while the frontend/backend are running. The default unconfigured coverage view correctly says **Not imported**.

## What was implemented

1. **Offline intake CLI:** `python -m backend.app.intake INPUT_DIRECTORY`. It reads one documented manifest/CSV schema, not a general ETL framework or an inferred provider schema.
2. **Stock list:** UTF-8 text or one-column CSV; case/whitespace normalization, duplicate counts and explicit mapping checks. Full-universe membership assertions are separate from the chosen candle sample. Current/undated assertions do not establish historical eligibility. Dated documentary review requires matching file hash, stock-option locator, session date and an explicit manual review reference.
3. **Candles:** exactly three selected equities plus NIFTY50 spot, nine five-minute intervals per series from 09:15 to 10:00 IST. Session date is configurable; normal-session confirmation is manual and sourced. Start/end semantics and timezone must be explicit. The 10:00-start row is outside the sample. Missing intervals are never filled. Conflicting duplicates invalidate coverage. Raw volume, missing equity volume, inapplicable index volume and actual zero are distinguished.
4. **Provenance:** actual ingestion/first-observation timestamps, separately attributed earlier acquisition claims, complete declared source metadata, SHA256s and distinct run directories. Prior run records are not overwritten. No historical `available_at` values are fabricated. Provider files are not read/retained while local retention permission is unresolved.
5. **Manual filing intake:** local document and structured metadata, source-page references, accounting scope, nullable revenue/profit-attributable-to-owners/diluted EPS. Exact/date-only/unknown publication precision stays distinct; exact time needs dissemination support. Manual reconciliation is never assigned automatically. YoY requires comparable units/quarters and a positive prior denominator; otherwise it remains null with a reason.
6. **Reports:** machine-readable JSON and concise text. Separate dimensions cover bars, mappings, metadata, review levels, filing precision and ingestion. Exit 0 means declared coverage complete, 1 partial/missing input, 2 invalid/failure. A synthetic complete report never establishes real-data success.
7. **Read-only coverage API and UI:** `/api/data-coverage` reads only the backend-configured report path. It exposes sanitized coverage, not documents, prices, financial values, source URLs, hashes or local paths. No upload, arbitrary-path reader, file browser or source fetch exists. The separate collapsible panel distinguishes not imported, invalid report, invalid inputs, partial, complete-synthetic and backend-error/recovery states. Dataset nature remains visible when collapsed.

## Recorded verification

These are actual local implementation-run results, not a new independent audit by the receiving AI. Environment: Python 3.12.16, Node 24.21.0, Chrome 156.0.8078.80.

| Command from checkout root | Result |
| --- | --- |
| `.venv/bin/python -m unittest discover -s backend/tests -v` | 45 passed: original 25 plus 20 new boundary tests. |
| `.venv/bin/python -m backend.app.validate` | Passed original M1 fixture validation. |
| `npm --prefix frontend test` | 12 passed. |
| `npm --prefix frontend run typecheck` | Passed. |
| `npm --prefix frontend run build` | Passed, 47 modules. |
| `.venv/bin/python scripts/check_http.py` | Passed M1 replay/proxy/health and separate no-import coverage route checks. |
| `npm --prefix frontend run test:browser` | 12 passed across desktop, tablet, mobile and 320px narrow viewports. |
| `.venv/bin/python -m backend.app.intake data/intake-example` | Exit 0, synthetic_test, 36 unique sample bars; one extra 10:00-start bar excluded. |
| `.venv/bin/python -m backend.app.intake data/intake-template` | Expected exit 1, partial, no real data or retained provider bytes. |
| CLI boundary tests | Verified ready/partial/invalid exits 0/1/2. |
| `git diff --cached --check` | Passed before commit. |

Browser tests used the actual importer and API and exercised all coverage states, backend shutdown/recovery, keyboard controls and unchanged M1 behavior. Desktop and narrow-mobile screenshots were inspected. Checked states had no axe accessibility violations or document-width overflow.

No required M2A software check remains unrun. Safari/Firefox, physical devices, a full assistive-technology audit and genuine market/source coverage were not tested. The pre-existing Starlette/httpx deprecation warning remains non-failing. Source identity, documentary accuracy, exchange calendar facts and permissions are not established by structural validation or file hashes.

## Main changed files

- `backend/app/intake/{schema,runner,filing,report,__main__}.py`
- `backend/app/coverage_api.py`, `backend/app/main.py`
- `frontend/src/coverage.ts`, `frontend/src/components/DataCoverage.tsx`, its CSS module, and the integration in `App.tsx`
- `backend/tests/test_intake.py`, frontend coverage tests/fixture, browser tests and `scripts/check_http.py`
- `data/intake-example/` (invented inputs) and `data/intake-template/` (blank user templates)
- `README.md`, `data/README.md`, `docs/API_CONTRACT.md`, `docs/MILESTONE_2A.md`, `docs/STATUS.md`

Full local code review command: `git diff main...feat/milestone-2a-local-intake`.

## What is actually pending

Please help the owner gather the smallest permitted local sample rather than add unrelated features:

1. **Stock list:** text or CSV, with source label and source/as-of date if known. Unknown dates stay unknown.
2. **Candles:** a locally retainable export for three selected equities (candidate mappings: INFY, RELIANCE, HDFCBANK) plus Nifty 50 spot, one confirmed normal session, 09:15–10:00 IST, nine completed intervals per series. Source, timestamp convention/timezone and price adjustment must be identified. The candidate session is 2026-10-30, subject to the supplied files and confirmation; no actual historical coverage is claimed.
3. **One filing:** permitted document plus manually entered company/period/basis/scope, source/page references and any sourced figures. Preserve actual publication precision. Exact dissemination evidence and dated stock-option listing evidence can follow later; the corresponding checks remain partial until supplied/reviewed.

A manually supplied list is useful but cannot alone pass historical documentary eligibility. Thirty-six candles alone cannot pass overall coverage. A date-only filing can be catalogued but cannot pass exact-publication coverage. No genuine input should be invented to make a panel green.

The previously proposed Infosys Q2 FY27 filing remains only a candidate source. It was not fetched or validated during implementation. Broker/data-provider access and retention rights have not been established. Do not treat earlier quoted vendor pricing as newly verified.

## Requested response from the coordinating AI

Please return:

- Whether this satisfies the intended M2A **software** scope, distinguishing any issue requiring code inspection.
- A short owner checklist for the actual input files and minimal metadata, using the implemented schema below.
- Any unresolved decision that truly blocks the sample, without turning optional enrichment into a prerequisite.
- If another coding step is necessary, a narrowly scoped continuation prompt that reads local status, preserves the feature branch and forbids pushing/deploying unless explicitly authorized.

## Appendix: exact implemented input/run documentation

The following is a snapshot of `docs/MILESTONE_2A.md` at handoff preparation. Repository documentation is the maintained source of truth; this appendix makes this single attachment usable without remote access to the feature branch.

---

# Milestone 2A — offline intake and coverage

Implemented 1 November 2026. **Software verification is separate from real-data coverage. No genuine market files were supplied.** The research desk still uses only M1 synthetic data. This importer never writes M1 eligibility/evidence records and never changes rankings or contract status.

## Run locally

Use the existing Python virtual environment and Node version in `.nvmrc`; no new dependencies are required. Commands below run from the repository root.

```sh
# Fully invented engineering example, including its documentary review records:
.venv/bin/python -m backend.app.intake data/intake-example

# Empty, cautious user-import template; expected exit 1 (partial):
.venv/bin/python -m backend.app.intake data/intake-template

# Actual inputs stay outside tracked data directories:
.venv/bin/python -m backend.app.intake /absolute/path/to/local-inputs
```

The CLI prints a concise report and the generated `private-data/imports/<UTC-time>-<unique-id>/report.json` path. Optional `--output-root private-data/my-imports` must remain inside this repository's ignored `private-data/`. Every run is new; old files are never overwritten. A missing input directory/file produces an actionable partial report rather than fictional data. Fix malformed material and run again.

| Exit | Meaning |
| --- | --- |
| 0 | `coverage_complete`: declared sample coverage and required manual reviews satisfied. For `synthetic_test`, this proves software behavior only. |
| 1 | `partial`: readable or absent material with coverage, source, retention, or documentary gaps. |
| 2 | `invalid`: malformed/contradictory inputs, or a command/output failure. Command failures print a diagnostic and may not create a report. |

Select a report **on the backend**, using the path printed by the command:

```sh
TRADE_COVERAGE_REPORT=private-data/imports/REPLACE-WITH-RUN-ID/report.json \
  .venv/bin/python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```

In another terminal run `nvm use` then `npm --prefix frontend run dev -- --port 5173 --strictPort`. Open http://127.0.0.1:5173/#data-coverage and expand **View coverage details**. **Refresh coverage** rereads the configured report; changing the environment variable requires restarting the backend. With the variable unset the panel says **Not imported**. Nothing automatically chooses the latest import or changes the synthetic research dataset.

## Input directory and strict schema

Use `data/intake-example/manifest.json` as a fully populated **synthetic** reference, or copy `data/intake-template/` into ignored `private-data/` before adding actual inputs. The blank template includes candidate mappings for INFY, RELIANCE, HDFCBANK and NIFTY50 spot; those mappings/session choices must be checked against the actual source. It supplies no prices, company figures, membership assertions or dissemination timestamps.

Input files are UTF-8 (CSV/text may have a BOM). Each file is capped at 10 MiB. JSON rejects duplicate properties, nonfinite values and unknown fields. CSV accepts exactly the documented headers, in any order; duplicate headers, extra/missing columns, malformed records and invalid numeric data fail validation. Files referenced by manifests must be regular files directly inside the input directory: no absolute paths, subdirectories, traversal or symlinks. Local filenames use letters/digits and `_.-`, starting with a letter/digit. Source URLs are stored as metadata only and are never fetched.

### `manifest.json` (`local-intake-v1`)

| Field | Accepted value / meaning |
| --- | --- |
| `schema_version` | Exactly `local-intake-v1`. |
| `dataset_id` | Required short label; identify the user's dataset, not a filename-derived identity. |
| `dataset_nature` | Required `synthetic_test` or `user_import`. Never inferred from the file name. |
| `source_label` | Required field, short label or `null` for unknown. |
| `source_url` | Optional public HTTP(S) URL without credentials, or null. Private metadata only. |
| `source_date`, `as_of_date` | Optional ISO dates or null. At least one known date is needed for complete provenance coverage; do not invent one. |
| `claimed_acquired` | Optional `{ "at": "offset-bearing ISO timestamp", "attribution": "who/what supports this earlier capture" }`. Must not be after actual ingestion or before a retained completed candle. Separate from application observation. |
| `session_date` | Required ISO date. Configurable; must not be in the future. The template proposes `2026-10-30`, not a verified historical-session claim. |
| `timezone` | Required `Asia/Kolkata`, the normalization/display timezone. |
| `source_timezone` | Required field: IANA timezone name, or null if every candle already has an offset. Naive times require an explicitly supplied valid timezone. Ambiguous/nonexistent DST times require offsets. |
| `sample_start`, `sample_end` | Required `09:15` and `10:00`. M2A deliberately supports this bounded opening sample only. |
| `interval_minutes` | Required `5`. |
| `timestamp_convention` | Required `bar_start` or `bar_end`. Never inferred. |
| `price_adjustment` | Required `adjusted`, `unadjusted`, or `unknown`. Unknown blocks complete provenance coverage. |
| `retention` | Required `permitted` or `unresolved`. |
| `retention_note` | Required field: note or null. `permitted` requires an actual local-use/retention note. |
| `normal_session_review`, `source_review` | Required `{ "confirmed": false, "reference": null }`, or true plus a supporting manual-review reference. These are user attestations, not automated calendar/source verification. |
| `instruments` | Required explicit mapping array (see below). |
| `stock_list` | Optional metadata object (see below), or null. |
| `filing` | `filing.json` or null. One filing only. |

Short public labels are 1–100 characters from letters, digits, spaces and `._()-`, starting with a letter/digit. Symbols are uppercase, up to 30 characters, with letters/digits and `&_.-`. References/retention notes are private text up to 1,000 characters. Do not put account data or credentials in labels or metadata.

Each instrument has **all** of:

```json
{"source_symbol":"NIFTY 50","symbol":"NIFTY50","exchange":"NSE","instrument_type":"spot_index","sample":true}
```

`instrument_type` is `equity` or `spot_index`; exchange is `NSE`. Source symbols are trimmed and uppercased. Both source symbols and canonical symbols must be unique; ambiguous aliases fail instead of selecting a match. Exactly three equity mappings and one NIFTY50 spot mapping must have `sample: true`. Additional explicit mappings with `sample: false` let a full universe list be recognized without requiring its candle coverage. There is no live exchange symbol resolver. Explicit mapping establishes identity as declared, not authoritative symbol verification.

### Stock list

Use `stocks.txt`, one NSE symbol per nonempty line, or `stocks.csv` with exactly one header, `symbol`. Whitespace/case are normalized. Duplicate symbols are removed and counted. Unmapped symbols remain in the private normalized list and are counted as unresolved mappings; company names/invalid symbol syntax fail with row context. Partial-list absence never means ineligible.

Manifest `stock_list`:

```json
{
  "file":"stocks.txt",
  "source_label":null,
  "source_date":null,
  "as_of_date":null,
  "evidence":[]
}
```

Dates remain null if unknown, independently of the actual import time. A list is a useful **user assertion** of options membership; current or undated assertions cannot establish past eligibility. A supporting evidence entry contains:

```json
{
  "symbol":"INFY",
  "document":"listing-evidence.csv",
  "sha256":"REPLACE_WITH_ACTUAL_64_CHARACTER_LOWERCASE_SHA256",
  "effective_date":"2026-10-30",
  "instrument_type":"stock_option",
  "contract_row":"Sheet/page/row identifying the stock-option contract",
  "review":{"confirmed":false,"reference":null}
}
```

The referenced bytes are hashed and retained if permitted; no speculative exchange-file parser is implemented. An actual matching hash gives `supporting_evidence`. A separately confirmed manual review for **the sample session date**, with a reference and stock-option row locator, is required for the dated-review check. Documentary review remains manual. A hash proves byte identity, not factual accuracy or permission. F&O ban status, listing membership and contract liquidity remain different questions.

### `candles.csv`

```csv
symbol,timestamp,open,high,low,close,volume
```

The symbol must match a manifest source mapping. Timestamps are ISO8601 and normalized to IST. For `bar_start`, 09:15 represents `[09:15,09:20)`; for `bar_end`, 09:20 represents the same interval. Offset-bearing UTC timestamps are accepted. Naive timestamps are accepted only with `source_timezone` supplied. Dates, alignment and completed interval ends are validated; wrong-session rows are invalid.

Each selected series expects exactly nine starts: 09:15, 09:20, …, 09:55. Total expected unique bars: **36**, with **3 equities and 1 context benchmark**. A 10:00-start row is outside the sample, retained/flagged but never counted toward the 36. Nonselected mapped instruments' bars are outside-sample rows too. Missing intervals stay missing. No forward-fill/interpolation.

OHLC must be finite and positive with `low <= open/close <= high`. Identical normalized duplicate candles are counted and deduplicated; conflicting duplicates make the run invalid and remove that interval from accepted coverage. The first identical raw fields are preserved; no conflicting last-row-wins behavior occurs.

`volume` is blank or a non-negative integer of at most 16 digits. `raw_volume` is preserved verbatim in normalized output. Blank equity volume is `missing`, normalized null, and a separate completeness gap; it does not delete the price bar. Blank spot-index volume is `not_applicable`, normalized null, and does not cause a price gap. An actual zero is preserved as zero with `provider_zero`; positive values are `reported`. There is no spot-index VWAP.

### `filing.json` (`local-filing-v1`)

This is manually entered metadata and optional values, not OCR, extraction or independent verification. Copy `filing.template.json` to `filing.json` in a private input directory and set manifest `filing` only after supplying the actual document.

Required fields: `schema_version` (`local-filing-v1`), selected equity `symbol`, `company`, `reporting_period`, ISO `quarter_end`, `accounting_basis`, `scope` (`consolidated` or `standalone`), `source_url` (URL or null), `document` (local basename), `source_pages`, `publication`, `transcription_status` (`unreviewed`, `transcribed`, `reconciled`). Optional `sha256` is checked against document bytes when supplied; the actual hash is always recorded. `claimed_acquired` has the same separately attributed form as the candle manifest. `reconciled` requires `reconciliation_reference`; it is a user's manual reconciliation claim, never assigned automatically.

Publication has exactly one precision:

```json
{"precision":"unknown"}
```

```json
{"precision":"date_only","date":"2026-10-20"}
```

```json
{
  "precision":"exact",
  "timestamp":"2026-10-20T10:00:00+05:30",
  "record_document":"dissemination-record.txt",
  "record_reference":"Actual exchange dissemination record locator"
}
```

These timestamps are **format examples**, not claims about Infosys publication. Exact precision requires identified support; a missing support document remains a coverage gap. Date-only data never becomes midnight. Unknown/date-only cannot carry an exact timestamp. Publication before the reporting quarter end, after actual ingestion, or a claimed acquisition before publication is rejected. Date comparisons use only the precision available. PDF creation, signatures, board-meeting end and press-conference times are not dissemination timestamps.

Optional figures are exactly `revenue`, `profit_attributable_to_owners`, and `diluted_eps`, each null or:

```json
{
  "unit":"INR million", "prior_unit":"INR million",
  "current":null, "prior":null,
  "current_period_end":"2026-09-30", "prior_period_end":"2025-09-30",
  "current_period_months":3, "prior_period_months":3,
  "page_row_reference":"Actual page and row"
}
```

All figures share the filing's accounting basis and scope. Do not enter total profit as profit attributable to owners; `total_profit` is an unsupported field. Values must be finite or null. YoY is calculated only with both figures, equal units, two three-month periods, the declared current quarter and its corresponding prior-year quarter, and a positive prior denominator. Otherwise the private normalized output has null plus `missing_figures`, `incomparable_units_or_periods`, `nonpositive_prior_denominator`, or `numeric_overflow`. Missing consensus, valuation, bullishness and scores are not inferred. At least one sourced current value is required for the filing-figure coverage check; other values can remain null, and a valid filing may have no computable YoY.

## Outputs, privacy and provenance

Every permitted run contains:

- `report.json`: `intake-run-v1` envelope, `coverage-v1` report, provenance and fixed file/row diagnostics.
- `report.txt`: concise human-readable dimensions and gaps.
- `originals/`: the bytes read during this run, including manifest, list, candles and supplied evidence/documents.
- `normalized.json`: parser/schema version, complete declared manifest/source metadata, SHA256s, separately attributed earlier acquisition claim, actual `first_observed_at`, normalized bars/list/evidence and manual filing/YoY results.

Run identifiers and genuine ingestion times change; normalized `data` and coverage counts reproduce from identical inputs. Observation time applies to the bytes obtained in that run, never to a historical candle close. Prior run provenance remains intact. No `available_at` is manufactured. With `retention: unresolved`, only the manifest is inspected to describe pending requirements; provider files are not read/hashed/copied and neither originals nor normalized provider output is stored. The generated pending report omits retained raw manifest/provenance. No acquisition is performed.

These files stay under ignored private storage. The API returns only a validated projection of `coverage`: identifiers/short source label, session/import time, sample counts/gaps, review levels and filing status. It excludes private manifest details, URLs, file paths, document hashes, raw bytes, prices, financial figures and references. It rejects unsupported/malformed/nonfinite or contradictory reports instead of inventing success. A local operator-created report is not a cryptographically authenticated source statement.

## Status semantics and required reviews

**Not imported** means no backend report is configured. A configured missing/unreadable/incompatible report is **Invalid report**, distinct from validly described **Invalid inputs** and an HTTP/backend failure. No fallback fixture data fills these states.

**Partial** includes missing intervals or files, unknown source dates/adjustment, unresolved symbol mappings, missing equity volume, pending normal-session/source review, missing dated eligibility review, missing filing, date-only/unknown publication, missing exact-publication support, missing filing source URL, or unreconciled transcription. Schema validity, price completeness, source review and documentary review are separate fields. Outside-window rows and identical duplicates are reported but do not alone prevent completion.

**Coverage complete** requires all nine accepted intervals per series plus required metadata/reviews and one sufficiently catalogued/reconciled filing with supported exact publication. It does not certify source accuracy, exchange eligibility, historical feed availability, licensing, profitability or option suitability. A **Synthetic test** complete report never establishes a successful real-data trial.

## Verification and remaining input

Run all README checks, including `npm --prefix frontend run test:browser`. The browser suite invokes the actual offline importer on invented fixtures, serves its sanitized report, and checks complete-synthetic, partial, invalid-input, invalid-report, no-import and API failure/recovery states. Desktop/mobile keyboard controls and accessibility/layout are checked. Software tests never count as genuine market coverage.

The smallest owner input remains:

1. A UTF-8 stock list (`stocks.txt` or one-column CSV), with optional source label/date.
2. A candle export that may be retained locally: three chosen equities plus Nifty 50 spot, one confirmed session, all nine five-minute intervals from 09:15–10:00 IST; identify source, timestamp convention/timezone and adjustment convention.
3. One permitted filing document plus manual metadata, page references, scope/units and publication evidence at its actual precision. An exact dissemination record can be supplied later; date-only intake stays partial.

Dated stock-option documentary evidence is needed before that review dimension can be complete. No broker credentials, authentication, scraping, paid API, deployment or scheduling is required or implemented.
