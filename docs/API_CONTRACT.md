# Milestone 1 API contract

API prefix `/api`. Development UI forwards `/api` to `http://127.0.0.1:8000`. No CORS wildcard, remote exposure or authentication required for this loopback-only prototype.

`GET /api/health` returns `{ "status": "ok", "mode": "synthetic_demo", "orders_enabled": false }`.

`GET /api/demo` returns:
```json
{
  "mode": "synthetic_demo",
  "label": "Synthetic demo data — not current market data",
  "source": "Bundled synthetic fixtures",
  "replay_times": ["2026-10-30T09:30:00+05:30", "2026-10-30T09:35:00+05:30", "2026-10-30T09:40:00+05:30"],
  "default_as_of": "2026-10-30T09:35:00+05:30"
}
```

`GET /api/replay?as_of=<URL encoded ISO8601 with offset>` returns this shape. All optional values are JSON null, not NaN. `rank` ranks only qualified screens, sorted by relative return descending with symbol as tie breaker. Other cards have null rank. ALL five fixture underlyings have cards, including exclusions.
```json
{
  "mode": "synthetic_demo",
  "as_of": "2026-10-30T09:35:00+05:30",
  "rule_version": "opening-range-v0.1",
  "source": "Bundled synthetic fixtures",
  "summary": {"total": 5, "qualified": 1, "watching": 1, "blocked": 3},
  "candidates": [{
    "symbol": "DEMO_ALPHA", "name": "Alpha Industries (fictional)", "sector": "Industrials",
    "rank": 1, "state": "qualified", "reason_codes": ["BREAKOUT_CONFIRMED"],
    "reasons": ["A completed close is above the first 15-minute range and relative return is positive."],
    "last_price": 103.0, "last_bar_end": "2026-10-30T09:35:00+05:30",
    "opening_range_high": 102.0, "opening_range_low": 99.0,
    "return_pct": 3.0, "benchmark_return_pct": 0.3, "relative_return_pct": 2.7,
    "eligibility": "eligible", "fundamentals_status": "available",
    "evidence": [{"id": "alpha-results-v1", "kind": "quarterly_result", "title": "Synthetic quarterly result",
      "summary": "Illustrative revenue growth, not a real company filing.", "period": "DEMO quarter",
      "source": "Synthetic fixture", "source_url": null,
      "published_at": "2026-10-30T08:30:00+05:30", "available_at": "2026-10-30T08:31:00+05:30"}],
    "bars": [{"bar_end":"2026-10-30T09:20:00+05:30","close":100.0}],
    "contract_status": "not_evaluated"
  }]
}
```

Allowed `state`: `qualified`, `watching`, `blocked`. Allowed `eligibility`: `eligible`, `ineligible`, `unknown`. `fundamentals_status`: `available`, `unknown`. API rejects naive/malformed timestamps with HTTP 422. Report invalid local datasets on startup with file/row errors. No HTTP upload route in this milestone. Backend CSV loader can read a custom directory through an explicit CLI validation command; default HTTP server always serves bundled synthetic fixtures to avoid mislabelling imported real data.

The prototype returns screens, not trade instructions. All contract statuses stay `not_evaluated`. No buy/sell buttons, option prices, lot sizes or returns are manufactured.
