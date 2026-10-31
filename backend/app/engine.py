"""Pure as-of replay. Screening priority is not a trade recommendation."""

import math
from datetime import datetime, time, timedelta

from .loader import IST
from .models import Bar, Dataset, Instrument

RULE_VERSION = "opening-range-v0.1"
MAX_AGE_SECONDS = 300
STEP = timedelta(minutes=5)
FUNDAMENTAL_KINDS = {"quarterly_result", "annual_result", "financial_statement"}


def known_bars(dataset: Dataset, symbol: str, as_of: datetime, start: datetime) -> list[Bar]:
    return sorted((bar for bar in dataset.bars if bar.symbol == symbol and
                   start <= bar.bar_start and bar.bar_end <= as_of and bar.available_at <= as_of and
                   bar.bar_start.date() == start.date()), key=lambda bar: bar.bar_end)


def availability(dataset: Dataset, symbol: str, as_of: datetime) -> str:
    records = [row for row in dataset.eligibility if row.symbol == symbol and
               row.available_at <= as_of and row.effective_from <= as_of and
               (row.effective_to is None or as_of < row.effective_to)]
    if not records:
        return "unknown"
    return max(records, key=lambda row: (row.available_at, row.effective_from)).status


def first_range(bars: list[Bar], start: datetime) -> list[Bar]:
    by_end = {bar.bar_end: bar for bar in bars}
    expected = [start + STEP * i for i in (1, 2, 3)]
    return [by_end[end] for end in expected if end in by_end and by_end[end].bar_start == end - STEP]


def has_gap(bars: list[Bar], start: datetime) -> bool:
    if not bars:
        return False
    available_ends = {bar.bar_end for bar in bars}
    expected_end = start + STEP
    while expected_end <= bars[-1].bar_end:
        if expected_end not in available_ends:
            return True
        expected_end += STEP
    return False


def candidate(dataset: Dataset, item: Instrument, benchmark_symbol: str | None,
              as_of: datetime, start: datetime) -> dict:
    bars = known_bars(dataset, item.symbol, as_of, start)
    latest = bars[-1] if bars else None
    evidence = sorted((row for row in dataset.evidence if row.symbol == item.symbol and
                       row.published_at <= as_of and row.available_at <= as_of),
                      key=lambda row: (row.available_at, row.id))
    status = availability(dataset, item.symbol, as_of)
    card = {
        "symbol": item.symbol, "name": item.name, "sector": item.sector,
        "rank": None, "state": "blocked", "reason_codes": [], "reasons": [],
        "last_price": latest.close if latest else None,
        "last_bar_end": latest.bar_end.isoformat() if latest else None,
        "opening_range_high": None, "opening_range_low": None,
        "return_pct": None, "benchmark_return_pct": None, "relative_return_pct": None,
        "eligibility": status,
        "fundamentals_status": "available" if any(row.kind in FUNDAMENTAL_KINDS for row in evidence) else "unknown",
        "evidence": [{"id": row.id, "kind": row.kind, "title": row.title,
                      "summary": row.summary, "period": row.period, "source": row.source,
                      "source_url": row.source_url, "published_at": row.published_at.isoformat(),
                      "available_at": row.available_at.isoformat()} for row in evidence],
        "bars": [{"bar_end": bar.bar_end.isoformat(), "close": bar.close} for bar in bars],
        "contract_status": "not_evaluated",
    }

    def reason(code: str, description: str) -> None:
        card["reason_codes"].append(code)
        card["reasons"].append(description)

    if status != "eligible":
        reason("OPTIONS_INELIGIBLE" if status == "ineligible" else "ELIGIBILITY_UNKNOWN",
               "Listed-options eligibility is ineligible at this time." if status == "ineligible" else
               "Listed-options eligibility is unknown at this time.")
    if latest is None:
        reason("NO_AVAILABLE_BARS", "No completed, available session bars.")
    elif (as_of - latest.bar_end).total_seconds() > MAX_AGE_SECONDS:
        reason("STALE_DATA", "The latest available completed bar is more than 300 seconds old.")
    opening_bars = first_range(bars, start)
    if len(opening_bars) != 3:
        reason("INCOMPLETE_OPENING_RANGE", "All three completed 09:15–09:30 bars must be available.")
    else:
        card["opening_range_high"] = max(bar.high for bar in opening_bars)
        card["opening_range_low"] = min(bar.low for bar in opening_bars)
    if has_gap(bars, start):
        reason("MISSING_BARS", "A five-minute session bar is missing before the latest available bar.")
    benchmark = known_bars(dataset, benchmark_symbol, as_of, start) if benchmark_symbol else []
    benchmark_range = first_range(benchmark, start)
    matching = next((bar for bar in benchmark if latest and bar.bar_end == latest.bar_end), None)
    if len(benchmark_range) != 3 or matching is None or has_gap(benchmark, start):
        reason("BENCHMARK_UNAVAILABLE", "The benchmark needs a complete range and a bar matching the stock's bar end.")
    elif (as_of - matching.bar_end).total_seconds() > MAX_AGE_SECONDS:
        reason("BENCHMARK_STALE", "The matching benchmark bar is more than 300 seconds old.")
    if card["reason_codes"]:
        return card
    # Both series use their session's first open and exactly the same end time.
    stock_return = (latest.close / opening_bars[0].open - 1) * 100
    benchmark_return = (matching.close / benchmark_range[0].open - 1) * 100
    relative = stock_return - benchmark_return
    if not all(math.isfinite(value) for value in (stock_return, benchmark_return, relative)):
        reason("NUMERIC_OVERFLOW", "Derived returns exceed the supported numeric range; metrics are unavailable.")
        return card
    card.update(return_pct=round(stock_return, 6), benchmark_return_pct=round(benchmark_return, 6),
                relative_return_pct=round(relative, 6))
    if latest.bar_end > start + STEP * 3 and latest.close > card["opening_range_high"] and relative > 0:
        card["state"] = "qualified"
        reason("BREAKOUT_CONFIRMED", "A completed close is above the first 15-minute range and relative return is positive.")
    else:
        card["state"] = "watching"
        if latest.bar_end <= start + STEP * 3:
            reason("WAITING_POST_RANGE_BAR", "The opening range is complete; wait for a subsequent completed bar.")
        if latest.bar_end > start + STEP * 3 and latest.close <= card["opening_range_high"]:
            reason("NO_BREAKOUT", "The latest completed close is not above the opening-range high.")
        if relative <= 0:
            reason("NO_RELATIVE_STRENGTH", "Session return does not exceed the benchmark at the same bar end.")
    return card


def replay(dataset: Dataset, as_of: datetime) -> dict:
    if as_of.tzinfo is None or as_of.utcoffset() is None:
        raise ValueError("as_of must include a timezone offset")
    as_of = as_of.astimezone(IST)
    start = datetime.combine(as_of.date(), time(9, 15), tzinfo=IST)
    known_instruments = [item for item in dataset.instruments if item.available_at <= as_of]
    benchmarks = sorted(item.symbol for item in known_instruments if item.kind == "benchmark")
    benchmark = benchmarks[0] if benchmarks else None
    cards = [candidate(dataset, item, benchmark, as_of, start) for item in known_instruments
             if item.kind == "underlying"]
    qualified = sorted((card for card in cards if card["state"] == "qualified"),
                       key=lambda card: (-card["relative_return_pct"], card["symbol"]))
    for rank, card in enumerate(qualified, 1):
        card["rank"] = rank
    cards.sort(key=lambda card: (0 if card["rank"] is not None else 1,
                                card["rank"] or 0, card["symbol"]))
    return {"mode": dataset.mode, "as_of": as_of.isoformat(), "rule_version": RULE_VERSION,
            "source": dataset.source,
            "summary": {"total": len(cards), "qualified": len(qualified),
                        "watching": sum(card["state"] == "watching" for card in cards),
                        "blocked": sum(card["state"] == "blocked" for card in cards)},
            "candidates": cards}
