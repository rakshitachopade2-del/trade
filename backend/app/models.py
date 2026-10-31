"""Immutable input records. Times must be timezone-aware."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class Instrument:
    symbol: str
    name: str
    sector: str
    kind: str
    available_at: datetime
    source: str


@dataclass(frozen=True, slots=True)
class Bar:
    symbol: str
    bar_start: datetime
    bar_end: datetime
    available_at: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int
    source: str


@dataclass(frozen=True, slots=True)
class Eligibility:
    symbol: str
    status: str
    effective_from: datetime
    effective_to: datetime | None
    available_at: datetime
    source: str


@dataclass(frozen=True, slots=True)
class Evidence:
    id: str
    symbol: str
    kind: str
    title: str
    summary: str
    period: str
    source: str
    source_url: str | None
    published_at: datetime
    available_at: datetime


@dataclass(frozen=True, slots=True)
class Dataset:
    instruments: tuple[Instrument, ...]
    bars: tuple[Bar, ...]
    eligibility: tuple[Eligibility, ...]
    evidence: tuple[Evidence, ...]
    mode: str
    source: str
