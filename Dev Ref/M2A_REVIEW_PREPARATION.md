# M2A review and private sample preparation

1 November 2026 (IST). **Software implemented; real-data validation pending. Application behavior unchanged.**

## Publication and sharing

The owner subsequently authorized commit and push. Reviewed implementation `9f0a1d04a534d741130217b74d8cc25c856d95b4` is published on [feat/milestone-2a-local-intake](https://github.com/rakshitachopade2-del/trade/tree/feat/milestone-2a-local-intake); main remains at the baseline below. These handoffs are a separate documentation update. No merge or deployment occurred.

Share this handoff and the committed review patch with the coordinating AI. For full implementation context, also share [M2A_AI_CHAT_HANDOFF.md](M2A_AI_CHAT_HANDOFF.md). **All artifacts/ and private-data/ links below are local-only:** those directories remain ignored and are not pushed. The reviewed patch contains no private inputs; private sample files/reports are not needed for the AI handoff.

Ask the AI to assess the financial-figure gate against the original optional-figures requirement, propose a narrowly scoped correction if warranted, and identify the smallest remaining genuine-input checklist. Do not rebuild completed features or treat the partial run as genuine-data validation.

## Review export

- Branch preserved: `feat/milestone-2a-local-intake`.
- Exact baseline: `a407e043e781d4d5e88794173f046c5d04ba6477`.
- Exact reviewed commit: `9f0a1d04a534d741130217b74d8cc25c856d95b4`.
- [Committed M2A review patch](../artifacts/reviews/m2a-9f0a1d0/M2A_committed_review.patch) — all 36 changed files, including new files and tests.
- Patch SHA256: `db05aa2150afd6864190c63d3c5e98006e6286695d65cef61361b7b2badd2018`.
- Command: `git diff --no-ext-diff --no-textconv --binary --full-index a407e043e781d4d5e88794173f046c5d04ba6477 9f0a1d04a534d741130217b74d8cc25c856d95b4 --`.
- [Export metadata](../artifacts/reviews/m2a-9f0a1d0/export-metadata.json) and [file inventory](../artifacts/reviews/m2a-9f0a1d0/changed-files.txt) retain the exact scope. Export is ignored by `.gitignore:4` (`artifacts/`).
- Credential-pattern scan and committed data inventory review found no credentials or private market inputs. Included data is explicitly synthetic examples or blank user templates. Uncommitted/ignored material is excluded.
- At task start: no tracked edits; only `Dev Ref/M2A_AI_CHAT_HANDOFF.md` untracked. It is preserved. This preparation adds this untracked handoff and a documentation-only `docs/STATUS.md` entry. During that bounded preparation nothing was committed, pushed, merged or reset; publication was authorized afterward as recorded above.

## Financial-figure finding — no behavior change

**One non-null current financial value gates overall `coverage_complete`, not only a separate dimension.**

- `backend/app/intake/schema.py:192` allows all three figure fields to be null.
- `backend/app/intake/runner.py:328` counts non-null current values; `:335` adds `filing_figures_missing` at zero; `:346` makes any gap produce overall partial.
- `backend/app/intake/report.py:134` rejects complete reports without figures. `frontend/src/coverage.ts:90` requires positive figures for complete responses too.
- Existing tests at `backend/tests/test_intake.py:205` and `:230` cover publication precision, missing values and unknown YoY, but do not directly assert the all-figures-absent overall status. Those two tests were run: **2 passed**; the existing Starlette/httpx deprecation warning is non-failing. The full suite was not rerun.
- [Focused probe](../artifacts/reviews/m2a-9f0a1d0/check_figure_gate.py), run with `.venv/bin/python artifacts/reviews/m2a-9f0a1d0/check_figure_gate.py`, confirmed: control has 36 bars and one figure, coverage complete; same inputs with all figures null remain schema-valid, with exact publication and reconciled filing, but produce **partial with only `filing_figures_missing`**. [Evidence JSON](../artifacts/reviews/m2a-9f0a1d0/figure-gate-evidence.json).
- This is stricter than the original permission to leave figures absent. Flagged for a later policy/code decision; deliberately unchanged. Synthetic probe files existed only in an isolated temporary directory, never in the genuine-input directory.

## Prepared sample and actual run

- Created [private-data/real-sample/](../private-data/real-sample/) from `data/intake-template/` because it did not exist. No existing inputs were overwritten. `.gitignore:18` (`private-data/`) verified.
- `dataset_nature=user_import`; candidate mappings INFY, RELIANCE, HDFCBANK and NIFTY50 spot preserved without eligibility claims.
- Empty `stocks.txt`, header-only `candles.csv`; no `filing.json` or filing document. Unconfigured `filing.template.json` has null figures and unknown publication.
- Retention unresolved; both manual reviews false. Source labels/URLs/dates and earlier-capture claims remain null. The private copy's provider `source_timezone` was set to null because it is unknown.
- Session `2026-10-30`, `bar_start` convention and filing-template company/period/scope remain candidate scaffolding, not verified source facts. Confirm from actual inputs before use; required convention has no unknown enum.
- Actual command: `.venv/bin/python -m backend.app.intake private-data/real-sample`.
- Actual exit **1**, **partial**, **0/36 bars**; nature **user_import**.
- [Generated report](../private-data/imports/20261101T120739858148Z-3d1ed43fb95b/report.json): `private-data/imports/20261101T120739858148Z-3d1ed43fb95b/report.json`. Adjacent `report.txt` is the human-readable version.
- [Saved CLI output](../artifacts/reviews/m2a-9f0a1d0/real-sample-cli.txt) and [run metadata/input hashes](../artifacts/reviews/m2a-9f0a1d0/real-sample-run.json) confirm the importer left source bytes unchanged.
- Actual gaps: `adjustment_unknown`, `eligibility_review_pending`, `filing_missing`, `missing_bars`, `retention_pending`, `session_review_pending`, `source_dates_unknown`, `source_review_pending`, `source_unknown`, `stock_list_missing`.
- With retention unresolved, only manifest requirements are examined: no provider files are read/hashed/copied and no normalized provider output is created. **This is not successful genuine-data validation.**

## Exactly what remains missing

1. Genuine stock list (`stocks.txt` or documented one-column CSV), plus source/date if known. A list alone is only an assertion.
2. Permitted `candles.csv`: nine five-minute intervals for each of three equities and Nifty spot. Source identity, source/as-of date, retention basis, adjustment convention, provider timezone/timestamp convention and source-symbol mapping need confirmation. Proposed session needs normal-opening confirmation/reference. No prices are present.
3. Dated stock-option documentary evidence for selected equities: actual document/hash, effective/session date, stock-option row locator and manual review/reference. None supplied; no historical eligibility claim is supported.
4. One actual filing document and configured `filing.json`: company/period/accounting basis/scope, source URL/pages, publication precision/support, transcription/reconciliation and separately attributed earlier capture only if known. Exact dissemination evidence is missing; date-only/unknown must stay at that precision.
5. All financial figures remain absent. Their optionality versus the implemented global gate is the unresolved finding above; do not fabricate a value to pass coverage. Units/comparable periods/source rows are needed only when genuine figures are supplied.

The bounded preparation made no application-source/dashboard changes, installed no dependencies and made no broker/MCP connection, external acquisition, credential request, purchase, AI API call, push, deployment, schedule or trade. The later owner-authorized Git publication is recorded above.
