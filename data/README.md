# Dataset contract

`synthetic/` contains invented values for five fictional stock underlyings and
one fictional benchmark. These are engineering fixtures, not historical NSE data,
investment evidence, current options eligibility or demonstrated trading results.

Validate the fixtures from the repository root:

```sh
python3 -m backend.app.validate
```

Validate a separate local directory using the same four CSV filenames:

```sh
python3 -m backend.app.validate /absolute/path/to/local/csv-directory
```

The command prints validation counts or file/row errors and exits nonzero on
failure. It does not import the data into the HTTP application. The HTTP server
always loads the bundled synthetic directory. A different directory is labelled
`unverified_import`, even if its contents were copied from the demo. Validation
does not authenticate a data source or establish licence rights. Keep actual
market data and personal account data out of the public repository.

## Files and fields

| File | Required columns |
| --- | --- |
| `instruments.csv` | `symbol,name,sector,kind,available_at,source` |
| `prices.csv` | `symbol,bar_start,bar_end,available_at,open,high,low,close,volume,source` |
| `eligibility.csv` | `symbol,status,effective_from,effective_to,available_at,source` |
| `evidence.csv` | `id,symbol,kind,title,summary,period,source,source_url,published_at,available_at` |

All times use ISO8601 with a timezone offset, for example
`2026-10-30T09:35:00+05:30`. The loader normalizes them to Asia/Kolkata. Blank
`effective_to` means no expiry; interval ends are exclusive. Blank `source_url`
means no external link. The synthetic files deliberately contain no fabricated
links to real filings. Other required values cannot be blank.

Instrument `kind` is `underlying` or `benchmark`; exactly one benchmark is
required. Eligibility `status` is `eligible`, `ineligible` or `unknown`.
Eligibility is usable only when published as available and currently effective.
A later available record supersedes an earlier one where intervals overlap;
contradictory overlapping records with identical availability times are rejected.

Bars must be exactly five minutes and start on five-minute boundaries. Prices
must be finite and positive, with `low <= open/close <= high`; volume is a
non-negative integer. Identical duplicate rows are deduplicated; conflicting
duplicates fail validation. Evidence cannot be available before publication.
Custom files should use actual source identifiers and actual first-usable times,
not backfilled guesses.

## Replay rules and limits

The opening range requires all three bars from 09:15 to 09:30 IST. A bar is
usable only when both its end and availability times have passed. Returns use
the first session open. Stock and benchmark returns use the same bar end;
relative return is their difference in **percentage points**. Required missing
bars or data older than 300 seconds block qualification. Exactly 300 seconds
is allowed; this is a fixture rule, not a production latency recommendation.

Only `quarterly_result`, `annual_result` and `financial_statement` evidence kinds
mark fundamentals as available. News alone does not. Evidence is informational
and never changes the first milestone's numerical ranking.

At 09:30 no stock has a post-range trigger; at 09:35 Alpha is the only qualifier.
At 09:40 Beta's synthetic quarterly result becomes visible. Gamma is ineligible,
Delta has unknown eligibility, and Epsilon has an incomplete opening range and
eventually stale data. All remain visible with exclusion reasons.

This schema lacks source revisions, exchange calendars, production quote quality,
instrument corporate-action handling, options chains and bid/ask fills. It is an
engineering starting point, not sufficient for real-market backtest conclusions.
