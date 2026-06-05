"""Export a scenario to static JSON so the dashboard can run with no backend.

This powers the hosted demo: the frontend falls back to this file when no API is
reachable, so the whole thing deploys as a static site.

    PYTHONPATH=src python scripts/export_scenario.py
"""

import json
from pathlib import Path

from medmaps.api.service import MedMapsService


def main() -> None:
    sc = MedMapsService().build_scenario(kind="event")
    out = Path("frontend/public/scenario.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(sc), encoding="utf-8")
    print(f"wrote {out} ({len(sc['frames'])} frames, {len(sc['actual'])} points)")


if __name__ == "__main__":
    main()
