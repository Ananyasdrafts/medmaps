"""Clinical evaluation of the chosen model (glass-box).

Reports the Clarke error grid, hypo/hyper event detection, and warning lead-time, on
the cached race cohort. Run from the repo root:
    PYTHONPATH=src python scripts/clinical.py
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from medmaps.config import load_config
from medmaps.data.windowing import windows_by_patient
from medmaps.eval.clinical import (
    clarke_zones,
    event_detection,
    lead_times,
    zone_percentages,
)
from medmaps.explain.glassbox import GlassBoxForecaster

FEATURES = ["cgm", "cho", "bolus", "basal"]
CACHE = Path("data/race_cohort.pkl")


def main() -> None:
    cfg = load_config()
    sm = cfg["data"]["sample_minutes"]
    input_steps = cfg["task"]["input_window_minutes"] // sm
    horizon_steps = max(cfg["task"]["horizons_minutes"]) // sm

    cohort = pd.read_pickle(CACHE)
    data = windows_by_patient(cohort, input_steps, horizon_steps, FEATURES, train_frac=0.7)
    x_tr, y_tr, x_te, y_te = data["X_train"], data["y_train"], data["X_test"], data["y_test"]

    model = GlassBoxForecaster(FEATURES, alpha=1.0).fit(x_tr, y_tr)
    pred = model.predict(x_te)

    zones = clarke_zones(y_te.ravel(), pred.ravel())
    pct = zone_percentages(zones)
    print("Clarke error grid (% of points):")
    print(f"  A {pct['A']}  B {pct['B']}  | A+B {pct['A'] + pct['B']:.2f}  "
          f"| dangerous C+D+E {pct['C'] + pct['D'] + pct['E']:.2f}")

    ev = event_detection(y_te, pred)
    print("\nhypo/hyper event detection (anywhere in 60-min horizon):")
    print(f"  sensitivity {ev['sensitivity']:.2f}  specificity {ev['specificity']:.2f}  "
          f"false-alarm {ev['false_alarm_rate']:.2f}")
    print(f"  (tp {ev['tp']}  fn {ev['fn']}  fp {ev['fp']}  tn {ev['tn']})")

    lt = lead_times(y_te, pred, sm)
    if len(lt):
        print(f"\nwarning lead-time: median {np.median(lt):.0f} min over {len(lt)} caught events")


if __name__ == "__main__":
    main()
