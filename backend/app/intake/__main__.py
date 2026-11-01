"""Usage: python -m backend.app.intake INPUT_DIR [--output-root private-data/imports]."""

import argparse
import sys
from pathlib import Path

from .runner import run_import


def main():
    parser = argparse.ArgumentParser(description='Offline local coverage intake; never feeds research rankings.')
    parser.add_argument('input_directory', type=Path)
    parser.add_argument('--output-root', type=Path, default=Path('private-data/imports'))
    args = parser.parse_args()
    private = Path(__file__).resolve().parents[3] / 'private-data'
    if not args.output_root.resolve().is_relative_to(private.resolve()):
        parser.error('output-root must be inside this repository private-data/ directory')
    try:
        destination, report = run_import(args.input_directory, args.output_root)
    except (OSError, ValueError) as exc:
        print(f'Intake could not write a run ({type(exc).__name__}); check the input and private-data output directory.', file=sys.stderr)
        return 2
    print((destination / 'report.txt').read_text(), end='')
    print(f'Report: {destination / "report.json"}')
    return {'coverage_complete': 0, 'partial': 1, 'invalid': 2}[report.status]


if __name__ == '__main__':
    raise SystemExit(main())
