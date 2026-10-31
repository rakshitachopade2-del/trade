"""Strict CSV loading; imports are validated, never served as synthetic data."""

import csv
import math
from datetime import datetime, timedelta
from pathlib import Path
from typing import Callable, TypeVar
from zoneinfo import ZoneInfo

from .models import Bar, Dataset, Eligibility, Evidence, Instrument

IST = ZoneInfo("Asia/Kolkata")
DEMO_DIRECTORY = Path(__file__).resolve().parents[2] / "data" / "synthetic"
# models live at repo/backend/app; parents[2] is repo.
T = TypeVar("T")


class DataValidationError(ValueError):
    def __init__(self, errors: list[str]):
        self.errors = errors
        super().__init__("Dataset validation failed:\n" + "\n".join(errors))


def parse_timestamp(value: str, field: str = "timestamp") -> datetime:
    try:
        parsed = datetime.fromisoformat(value)
    except (ValueError, TypeError):
        raise ValueError(f"{field}: expected an ISO8601 timestamp with a timezone offset") from None
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"{field}: timezone offset is required (for example +05:30)")
    try:
        return parsed.astimezone(IST)
    except (OverflowError, ValueError):
        raise ValueError(f"{field}: timestamp is outside the supported date range") from None


def required(row: dict, field: str) -> str:
    value = row.get(field)
    if value is None or not value.strip():
        raise ValueError(f"{field}: value is required")
    return value.strip()


def stamp(row: dict, field: str) -> datetime:
    return parse_timestamp(required(row, field), field)


def number(row: dict, field: str) -> float:
    try:
        value = float(required(row, field))
    except ValueError:
        raise ValueError(f"{field}: expected a finite positive number") from None
    if not math.isfinite(value) or value <= 0:
        raise ValueError(f"{field}: expected a finite positive number")
    return value


def enum(row: dict, field: str, allowed: set[str]) -> str:
    value = required(row, field)
    if value not in allowed:
        raise ValueError(f"{field}: expected one of {', '.join(sorted(allowed))}")
    return value


def instrument(row: dict) -> Instrument:
    return Instrument(required(row, "symbol"), required(row, "name"), required(row, "sector"),
                      enum(row, "kind", {"underlying", "benchmark"}),
                      stamp(row, "available_at"), required(row, "source"))


def bar(row: dict) -> Bar:
    start, end = stamp(row, "bar_start"), stamp(row, "bar_end")
    if end - start != timedelta(minutes=5):
        raise ValueError("bar_end: this rule requires exactly 5-minute bars")
    if start.second or start.microsecond or start.minute % 5:
        raise ValueError("bar_start: must align to a 5-minute boundary")
    available = stamp(row, "available_at")
    if available < start:
        raise ValueError("available_at: cannot precede bar_start")
    opening, high, low, close = (number(row, field) for field in ("open", "high", "low", "close"))
    if low > high or not low <= opening <= high or not low <= close <= high:
        raise ValueError("OHLC: low <= open/close <= high is required")
    try:
        volume = int(required(row, "volume"))
    except ValueError:
        raise ValueError("volume: expected a non-negative integer") from None
    if volume < 0:
        raise ValueError("volume: expected a non-negative integer")
    return Bar(required(row, "symbol"), start, end, available, opening, high, low, close,
               volume, required(row, "source"))


def eligibility(row: dict) -> Eligibility:
    start = stamp(row, "effective_from")
    end = parse_timestamp(row["effective_to"], "effective_to") if row["effective_to"].strip() else None
    if end is not None and end <= start:
        raise ValueError("effective_to: must be later than effective_from; interval end is exclusive")
    return Eligibility(required(row, "symbol"), enum(row, "status", {"eligible", "ineligible", "unknown"}),
                       start, end, stamp(row, "available_at"), required(row, "source"))


def evidence(row: dict) -> Evidence:
    published, available = stamp(row, "published_at"), stamp(row, "available_at")
    if available < published:
        raise ValueError("available_at: cannot precede published_at")
    url = row["source_url"].strip() or None
    if url and not url.startswith(("https://", "http://")):
        raise ValueError("source_url: expected http(s) URL or an empty field")
    return Evidence(required(row, "id"), required(row, "symbol"), required(row, "kind"),
                    required(row, "title"), required(row, "summary"), required(row, "period"),
                    required(row, "source"), url, published, available)


def read_records(directory: Path, filename: str, fields: list[str], parser: Callable[[dict], T],
                 key: Callable[[T], object], errors: list[str]) -> tuple[T, ...]:
    path = directory / filename
    seen: dict[object, tuple[T, int]] = {}
    try:
        with path.open(newline="", encoding="utf-8-sig") as handle:
            reader = csv.DictReader(handle)
            headers = reader.fieldnames or []
            duplicates = {field for field in headers if headers.count(field) > 1}
            if duplicates:
                errors.append(f"{filename}:row 1: duplicate columns: {', '.join(sorted(duplicates))}")
                return ()
            missing = set(fields) - set(reader.fieldnames or [])
            if missing:
                errors.append(f"{filename}:row 1: missing columns: {', '.join(sorted(missing))}")
                return ()
            for row_number, row in enumerate(reader, start=2):
                try:
                    if None in row or any(row.get(field) is None for field in fields):
                        raise ValueError("column count does not match header")
                    item = parser(row)
                    item_key = key(item)
                    previous = seen.get(item_key)
                    if previous and previous[0] != item:
                        raise ValueError(f"conflicting duplicate of row {previous[1]} for {item_key}")
                    seen.setdefault(item_key, (item, row_number))
                except (ValueError, TypeError, KeyError) as exc:
                    errors.append(f"{filename}:row {row_number}: {exc}")
    except (OSError, UnicodeError, csv.Error) as exc:
        errors.append(f"{filename}: {exc}")
    return tuple(item for item, _ in seen.values())


def load_dataset(directory: Path | str = DEMO_DIRECTORY) -> Dataset:
    directory = Path(directory).resolve()
    errors: list[str] = []
    instruments = read_records(directory, "instruments.csv", list(Instrument.__dataclass_fields__),
                               instrument, lambda x: x.symbol, errors)
    bars = read_records(directory, "prices.csv", list(Bar.__dataclass_fields__), bar,
                        lambda x: (x.symbol, x.bar_start, x.bar_end), errors)
    eligibility_rows = read_records(directory, "eligibility.csv", list(Eligibility.__dataclass_fields__),
                                    eligibility, lambda x: (x.symbol, x.effective_from, x.available_at), errors)
    evidence_rows = read_records(directory, "evidence.csv", list(Evidence.__dataclass_fields__), evidence,
                                lambda x: x.id, errors)
    symbols = {item.symbol for item in instruments}
    for filename, records in (("prices.csv", bars), ("eligibility.csv", eligibility_rows),
                              ("evidence.csv", evidence_rows)):
        for item in records:
            if item.symbol not in symbols:
                errors.append(f"{filename}: symbol {item.symbol!r} is absent from instruments.csv")
    if sum(item.kind == "benchmark" for item in instruments) != 1:
        errors.append("instruments.csv: exactly one benchmark instrument is required")
    if not bars:
        errors.append("prices.csv: at least one valid price bar is required")
    # Later publications explicitly supersede older known eligibility; two
    # contradictory statuses published simultaneously have no reliable winner.
    for index, left in enumerate(eligibility_rows):
        for right in eligibility_rows[index + 1:]:
            if left.symbol != right.symbol or left.available_at != right.available_at or left.status == right.status:
                continue
            overlap = ((left.effective_to is None or right.effective_from < left.effective_to) and
                       (right.effective_to is None or left.effective_from < right.effective_to))
            if overlap:
                errors.append(f"eligibility.csv: contradictory overlapping intervals for {left.symbol} "
                              f"with the same available_at {left.available_at.isoformat()}")
    if errors:
        raise DataValidationError(errors)
    is_demo = directory == DEMO_DIRECTORY.resolve()
    return Dataset(instruments, bars, eligibility_rows, evidence_rows,
                   "synthetic_demo" if is_demo else "unverified_import",
                   "Bundled synthetic fixtures" if is_demo else f"Validated local CSV directory: {directory.name}")
