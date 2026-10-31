"""CLI only: validate local CSV data without importing it into the HTTP demo."""

import argparse
import json
import sys
from pathlib import Path

from .loader import DEMO_DIRECTORY, DataValidationError, load_dataset


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", nargs="?", type=Path, default=DEMO_DIRECTORY)
    args = parser.parse_args()
    try:
        dataset = load_dataset(args.directory)
    except DataValidationError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(json.dumps({"status": "valid", "mode": dataset.mode, "source": dataset.source,
                      "instruments": len(dataset.instruments), "bars": len(dataset.bars),
                      "eligibility_records": len(dataset.eligibility), "evidence_records": len(dataset.evidence)},
                     indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
