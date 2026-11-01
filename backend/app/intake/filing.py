"""Manual transcription only. Computed comparisons are not source verification."""

import math
from datetime import datetime

from .schema import Filing, Figure
from ..loader import IST


def yoy(figure: Figure | None, quarter_end) -> dict:
    if figure is None or figure.current is None or figure.prior is None:
        return {'value_pct': None, 'reason': 'missing_figures'}
    if (figure.unit != figure.prior_unit or figure.current_period_months != 3 or figure.prior_period_months != 3
        or figure.current_period_end != quarter_end
        or (figure.prior_period_end.year, figure.prior_period_end.month, figure.prior_period_end.day)
        != (quarter_end.year - 1, quarter_end.month, quarter_end.day)):
        return {'value_pct': None, 'reason': 'incomparable_units_or_periods'}
    if figure.prior <= 0:
        return {'value_pct': None, 'reason': 'nonpositive_prior_denominator'}
    result = (figure.current / figure.prior - 1) * 100
    if not math.isfinite(result):
        return {'value_pct': None, 'reason': 'numeric_overflow'}
    return {'value_pct': round(result, 6), 'reason': None}


def validate_times(filing: Filing, observed: datetime) -> None:
    if filing.quarter_end > observed.astimezone(IST).date():
        raise ValueError('quarter ends after import')
    publication = filing.publication
    at = publication.timestamp
    day = at.astimezone(IST).date() if at else publication.date
    if day and (day < filing.quarter_end or day > observed.astimezone(IST).date()):
        raise ValueError('publication date is outside quarter-end/import bounds')
    if at and at > observed:
        raise ValueError('publication is after import')
    claim = filing.claimed_acquired
    if claim:
        if claim.at > observed or claim.at.astimezone(IST).date() < filing.quarter_end or (at and claim.at < at) or (day and claim.at.astimezone(IST).date() < day):
            raise ValueError('claimed capture contradicts publication/import')


def normalize_filing(filing: Filing, document_hash: str) -> dict:
    result = filing.model_dump(mode='json')
    result['sha256'] = document_hash
    result['verification'] = 'manual_metadata_only'
    result['yoy'] = {name: yoy(getattr(filing, name), filing.quarter_end)
                     for name in ('revenue', 'profit_attributable_to_owners', 'diluted_eps')}
    return result
