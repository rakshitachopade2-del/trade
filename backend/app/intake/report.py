"""Small public report contract: no raw prices, documents, URLs or local paths."""

from datetime import date, datetime
from typing import Literal

from pydantic import Field, field_validator, model_validator

from .schema import Label, Model, Symbol

Gap = Literal['manifest_missing', 'manifest_invalid', 'retention_pending', 'candles_missing',
              'invalid_rows', 'missing_bars', 'mapping_unknown', 'source_unknown',
              'source_dates_unknown', 'adjustment_unknown', 'source_review_pending',
              'session_review_pending', 'stock_list_missing', 'stock_list_unmapped',
              'eligibility_review_pending', 'filing_missing', 'filing_publication_partial',
              'filing_reconciliation_pending', 'filing_figures_missing', 'filing_source_unknown',
              'equity_volume_missing']


class Series(Model):
    symbol: Symbol
    instrument_type: Literal['equity', 'spot_index']
    expected: int = Field(ge=1, le=9)
    present: int = Field(ge=0, le=9)
    missing: list[str] = Field(max_length=9)
    duplicates: int = Field(ge=0)
    outside_window: int = Field(ge=0)
    missing_volume: int = Field(ge=0, le=9)

    @model_validator(mode='after')
    def counts(self):
        if self.expected != 9 or self.present + len(self.missing) != self.expected or len(set(self.missing)) != len(self.missing):
            raise ValueError('inconsistent interval counts')
        if any(t not in [f'09:{m:02d}' for m in range(15, 60, 5)] for t in self.missing):
            raise ValueError('invalid missing interval')
        if self.missing_volume > self.present:
            raise ValueError('inconsistent volume count')
        return self


class Membership(Model):
    symbol: Symbol
    level: Literal['unknown', 'user_assertion', 'supporting_evidence']
    dated_review: bool

    @model_validator(mode='after')
    def review(self):
        if self.dated_review and self.level != 'supporting_evidence':
            raise ValueError('review requires documentary evidence')
        return self


class FilingSummary(Model):
    status: Literal['not_imported', 'imported']
    symbol: Symbol | None = None
    publication_precision: Literal['exact', 'date_only', 'unknown'] = 'unknown'
    reconciliation: Literal['unreviewed', 'transcribed', 'reconciled'] = 'unreviewed'
    figures_present: int = Field(default=0, ge=0, le=3)
    source_known: bool = False

    @model_validator(mode='after')
    def presence(self):
        if self.status == 'not_imported' and (self.symbol is not None or self.publication_precision != 'unknown' or self.reconciliation != 'unreviewed' or self.figures_present or self.source_known):
            raise ValueError('absent filing cannot contain evidence')
        if self.status == 'imported' and self.symbol is None:
            raise ValueError('imported filing requires symbol')
        return self


class Coverage(Model):
    schema_version: Literal['coverage-v1']
    parser_version: Literal['local-intake-v1']
    status: Literal['partial', 'invalid', 'coverage_complete']
    dataset_id: Label | None
    dataset_nature: Literal['synthetic_test', 'user_import'] | None
    source_label: Label | None
    session_date: date | None
    imported_at: datetime
    stock_count: int = Field(ge=0, le=3)
    benchmark: Literal['NIFTY50'] | None
    series: list[Series] = Field(max_length=4)
    membership: list[Membership] = Field(max_length=3)
    universe_count: int = Field(ge=0)
    list_duplicates: int = Field(ge=0)
    unmapped_symbols: int = Field(ge=0)
    invalid_rows: int = Field(ge=0)
    outside_window: int = Field(ge=0)
    duplicate_rows: int = Field(ge=0)
    schema_valid: bool
    source_review: Literal['pending', 'manual_confirmed']
    session_review: Literal['pending', 'manual_confirmed']
    price_adjustment: Literal['adjusted', 'unadjusted', 'unknown']
    source_dates_known: bool
    retention: Literal['permitted', 'unresolved']
    filing: FilingSummary
    gaps: list[Gap] = Field(max_length=30)

    @field_validator('imported_at')
    @classmethod
    def aware(cls, value):
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError('import time requires an offset')
        return value

    @model_validator(mode='after')
    def consistent(self):
        equities = [s.symbol for s in self.series if s.instrument_type == 'equity']
        indices = [s.symbol for s in self.series if s.instrument_type == 'spot_index']
        if self.series:
            if self.dataset_id is None or self.dataset_nature is None or self.session_date is None:
                raise ValueError('declared sample requires dataset and session identity')
            if len(set(s.symbol for s in self.series)) != 4 or len(equities) != 3 or indices != ['NIFTY50'] or self.stock_count != 3 or self.benchmark != 'NIFTY50':
                raise ValueError('inconsistent sample')
            if {m.symbol for m in self.membership} != set(equities) or len(self.membership) != 3:
                raise ValueError('inconsistent membership')
        elif self.stock_count or self.benchmark or self.membership:
            raise ValueError('missing sample')
        if self.filing.status == 'imported' and self.filing.symbol not in equities:
            raise ValueError('filing must belong to a selected equity')
        if len(set(self.gaps)) != len(self.gaps):
            raise ValueError('duplicate gap codes')
        if self.outside_window < sum(s.outside_window for s in self.series) or self.duplicate_rows < sum(s.duplicates for s in self.series):
            raise ValueError('inconsistent row totals')
        if self.invalid_rows and self.status != 'invalid':
            raise ValueError('invalid rows require invalid status')
        if self.schema_valid == (self.status == 'invalid'):
            raise ValueError('inconsistent schema status')
        if self.status == 'coverage_complete':
            if (self.gaps or len(self.series) != 4 or any(s.present != 9 or (s.instrument_type == 'equity' and s.missing_volume) for s in self.series)
                or self.invalid_rows or self.unmapped_symbols or not all(m.dated_review for m in self.membership)
                or self.source_review != 'manual_confirmed' or self.session_review != 'manual_confirmed'
                or self.price_adjustment == 'unknown' or not self.source_dates_known or self.retention != 'permitted'
                or not self.source_label or not self.dataset_id or not self.dataset_nature or not self.session_date
                or self.filing.status != 'imported' or self.filing.publication_precision != 'exact'
                or self.filing.reconciliation != 'reconciled' or not self.filing.figures_present or not self.filing.source_known):
                raise ValueError('complete report lacks required coverage or reviews')
        elif not self.gaps:
            raise ValueError('incomplete report requires gaps')
        return self
