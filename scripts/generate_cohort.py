"""Pre-build the demo cohort cache so the first API call is instant.

    PYTHONPATH=src python scripts/generate_cohort.py
"""

from medmaps.api.service import load_cohort
from medmaps.config import load_config


def main() -> None:
    df = load_cohort(load_config())
    print(f"cohort ready: {len(df)} rows across {df['patient'].nunique()} patients")


if __name__ == "__main__":
    main()
