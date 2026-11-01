"""Versioned local input contracts. No provider schema or calendar is inferred."""

from datetime import date as Date, datetime
from typing import Annotated, Literal
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, field_validator, model_validator

Label = Annotated[str, StringConstraints(min_length=1, max_length=100, pattern=r'^[A-Za-z0-9][A-Za-z0-9 ._()-]*$')]
Symbol = Annotated[str, StringConstraints(min_length=1, max_length=30, pattern=r'^[A-Z0-9][A-Z0-9&_.-]*$')]
Filename = Annotated[str, StringConstraints(min_length=1, max_length=80, pattern=r'^[A-Za-z0-9][A-Za-z0-9_.-]*$')]
Note = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=1000)]
Hash = Annotated[str, StringConstraints(pattern=r'^[a-f0-9]{64}$')]


class Model(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True, allow_inf_nan=False)


class Claim(Model):
    at: datetime
    attribution: Note

    @field_validator('at')
    @classmethod
    def aware(cls, value):
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError('timezone offset required')
        return value


class Review(Model):
    confirmed: bool = False
    reference: Note | None = None

    @model_validator(mode='after')
    def require_reference(self):
        if self.confirmed and not self.reference:
            raise ValueError('confirmed reviews need a reference')
        return self


class Instrument(Model):
    source_symbol: Annotated[str, StringConstraints(min_length=1, max_length=40)]
    symbol: Symbol
    exchange: Literal['NSE']
    instrument_type: Literal['equity', 'spot_index']
    sample: bool

    @field_validator('source_symbol')
    @classmethod
    def normalized(cls, value):
        if not value.strip() or any(ord(char) < 32 for char in value):
            raise ValueError('source symbol must be nonempty and contain no control characters')
        return value.strip().upper()


class EligibilityEvidence(Model):
    symbol: Symbol
    document: Filename
    sha256: Hash
    effective_date: Date
    instrument_type: Literal['stock_option']
    contract_row: Note
    review: Review


class StockList(Model):
    file: Literal['stocks.txt', 'stocks.csv']
    source_label: Label | None = None
    source_date: Date | None = None
    as_of_date: Date | None = None
    evidence: list[EligibilityEvidence] = Field(default_factory=list, max_length=1000)


class Manifest(Model):
    schema_version: Literal['local-intake-v1']
    dataset_id: Label
    dataset_nature: Literal['synthetic_test', 'user_import']
    source_label: Label | None
    source_url: str | None = None
    source_date: Date | None = None
    as_of_date: Date | None = None
    claimed_acquired: Claim | None = None
    session_date: Date
    timezone: Literal['Asia/Kolkata']
    source_timezone: str | None
    sample_start: Literal['09:15']
    sample_end: Literal['10:00']
    interval_minutes: Literal[5]
    timestamp_convention: Literal['bar_start', 'bar_end']
    price_adjustment: Literal['adjusted', 'unadjusted', 'unknown']
    retention: Literal['permitted', 'unresolved']
    retention_note: Note | None
    normal_session_review: Review
    source_review: Review
    instruments: list[Instrument] = Field(min_length=4, max_length=1000)
    stock_list: StockList | None = None
    filing: Literal['filing.json'] | None = None

    @field_validator('source_timezone')
    @classmethod
    def valid_zone(cls, value):
        if value is not None:
            try:
                ZoneInfo(value)
            except (ZoneInfoNotFoundError, ValueError):
                raise ValueError('unrecognized source timezone') from None
        return value

    @field_validator('source_url')
    @classmethod
    def public_url(cls, value):
        # Recorded only; never fetched or exposed by the report API.
        if value is not None:
            from urllib.parse import urlsplit
            url = urlsplit(value)
            if url.scheme not in ('https', 'http') or not url.hostname or url.username or url.password:
                raise ValueError('expected a public http(s) URL without credentials')
        return value

    @model_validator(mode='after')
    def mappings(self):
        if len({i.source_symbol for i in self.instruments}) != len(self.instruments):
            raise ValueError('ambiguous source symbol mapping')
        if len({i.symbol for i in self.instruments}) != len(self.instruments):
            raise ValueError('ambiguous canonical symbol mapping')
        chosen = [i for i in self.instruments if i.sample]
        if sum(i.instrument_type == 'equity' for i in chosen) != 3 or sum(i.instrument_type == 'spot_index' for i in chosen) != 1:
            raise ValueError('sample requires exactly three equities and one spot index')
        if next(i.symbol for i in chosen if i.instrument_type == 'spot_index') != 'NIFTY50':
            raise ValueError('benchmark must explicitly map to NIFTY50 spot')
        if self.retention == 'permitted' and not self.retention_note:
            raise ValueError('permitted local retention needs a note')
        return self


class Publication(Model):
    precision: Literal['exact', 'date_only', 'unknown']
    timestamp: datetime | None = None
    date: Date | None = None
    record_document: Filename | None = None
    record_reference: Note | None = None

    @field_validator('timestamp')
    @classmethod
    def aware(cls, value):
        if value is not None and (value.tzinfo is None or value.utcoffset() is None):
            raise ValueError('exact publication requires a timezone offset')
        return value

    @model_validator(mode='after')
    def precision_matches(self):
        if self.precision == 'exact':
            if self.timestamp is None or self.date is not None or not self.record_document or not self.record_reference:
                raise ValueError('exact publication needs a timestamp and dissemination record, not a date')
        elif self.timestamp is not None or self.record_document is not None or self.record_reference is not None:
            raise ValueError('do not manufacture exact publication metadata')
        if (self.precision == 'date_only') != (self.date is not None):
            raise ValueError('date-only publication needs only a date')
        return self


class Figure(Model):
    unit: Label
    prior_unit: Label
    current: float | None
    prior: float | None
    current_period_end: Date
    prior_period_end: Date
    current_period_months: int = Field(ge=1, le=12)
    prior_period_months: int = Field(ge=1, le=12)
    page_row_reference: Note


class Filing(Model):
    schema_version: Literal['local-filing-v1']
    symbol: Symbol
    company: Label
    reporting_period: Label
    quarter_end: Date
    accounting_basis: Label
    scope: Literal['consolidated', 'standalone']
    source_url: str | None
    document: Filename
    sha256: Hash | None = None
    source_pages: Note
    publication: Publication
    claimed_acquired: Claim | None = None
    transcription_status: Literal['unreviewed', 'transcribed', 'reconciled']
    reconciliation_reference: Note | None = None
    revenue: Figure | None = None
    profit_attributable_to_owners: Figure | None = None
    diluted_eps: Figure | None = None

    _url = field_validator('source_url')(Manifest.public_url.__func__)

    @model_validator(mode='after')
    def reconciliation(self):
        if self.transcription_status == 'reconciled' and not self.reconciliation_reference:
            raise ValueError('manual reconciliation needs a reference')
        return self
