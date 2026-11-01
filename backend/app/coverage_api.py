"""Read one operator-configured report. Never accept a path from an HTTP caller."""

import os
from pathlib import Path

from .intake.report import Coverage
from .intake.runner import strict_json


def data_coverage():
    configured = os.environ.get('TRADE_COVERAGE_REPORT')
    empty = {'api_version': 'coverage-api-v1', 'state': 'not_imported', 'report': None}
    if not configured:
        return empty
    try:
        with Path(configured).open('rb') as handle:
            raw = handle.read(2 * 1024 * 1024 + 1)
        if len(raw) > 2 * 1024 * 1024:
            raise ValueError()
        envelope = strict_json(raw)
        if not isinstance(envelope, dict) or envelope.get('schema_version') != 'intake-run-v1':
            raise ValueError()
        import json
        report = Coverage.model_validate_json(json.dumps(envelope['coverage'], allow_nan=False))
        return {'api_version': 'coverage-api-v1', 'state': 'report', 'report': report.model_dump(mode='json')}
    except (OSError, ValueError, KeyError, TypeError, OverflowError, RecursionError):
        return {**empty, 'state': 'invalid_report'}
