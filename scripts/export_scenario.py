"""Export several scenarios to static JSON so the dashboard varies with no backend.

Uses a slightly larger in-memory cohort (not the cached one) so the demo has a few
distinct patients to cycle through. Powers the hosted static demo.

    PYTHONPATH=src python scripts/export_scenario.py
"""

import json
from pathlib import Path

from medmaps.api.service import MedMapsService
from medmaps.config import load_config
from medmaps.data.simulate import simulate_cohort

NAMES = [
    "adolescent#001", "adult#001", "child#001",
    "adolescent#002", "adult#002", "child#002",
]


def main() -> None:
    cfg = load_config()
    cohort = simulate_cohort(NAMES, 4, cfg["data"]["sample_minutes"],
                             missed_bolus_prob=0.1, seed=cfg["seed"])
    scenarios = MedMapsService(cohort=cohort).all_scenarios()
    out = Path("frontend/public/scenarios.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(scenarios), encoding="utf-8")
    print(f"wrote {out} ({len(scenarios)} scenarios)")


if __name__ == "__main__":
    main()
