"""Run the model race: generate a small cohort, window it leakage-free, fit the
baselines, and report RMSE at the 30 and 60 minute horizons.

Cohort is cached so reruns are instant. Run from the repo root:
    PYTHONPATH=src python scripts/race.py
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from medmaps.config import load_config
from medmaps.data.simulate import simulate_cohort
from medmaps.data.windowing import windows_by_patient
from medmaps.eval.metrics import rmse, rmse_per_horizon
from medmaps.models.baselines import NaivePersistence, NaiveTrend, RidgeLagged

COHORT = ["adolescent#001", "adult#001", "child#001"]
DAYS = 4
FEATURES = ["cgm", "cho", "bolus", "basal"]
CACHE = Path("data/race_cohort.pkl")


def get_cohort(sample_minutes: int, seed: int) -> pd.DataFrame:
    if CACHE.exists():
        return pd.read_pickle(CACHE)
    df = simulate_cohort(COHORT, DAYS, sample_minutes, missed_bolus_prob=0.1, seed=seed)
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    df.to_pickle(CACHE)
    return df


def main() -> pd.DataFrame:
    cfg = load_config()
    sm = cfg["data"]["sample_minutes"]
    input_steps = cfg["task"]["input_window_minutes"] // sm
    horizons = cfg["task"]["horizons_minutes"]
    horizon_steps = max(horizons) // sm

    cohort = get_cohort(sm, cfg["seed"])
    data = windows_by_patient(cohort, input_steps, horizon_steps, FEATURES, train_frac=0.7)
    x_tr, y_tr, x_te, y_te = data["X_train"], data["y_train"], data["X_test"], data["y_test"]
    print(f"cohort: {len(COHORT)} patients x {DAYS}d | train windows: {len(x_tr)} | "
          f"test windows: {len(x_te)}")

    cgm_idx = FEATURES.index("cgm")
    models = [
        NaivePersistence(target_index=cgm_idx),
        NaiveTrend(target_index=cgm_idx),
        RidgeLagged(alpha=1.0),
    ]
    rows = []
    for model in models:
        model.fit(x_tr, y_tr)
        pred = model.predict(x_te)
        per_h = rmse_per_horizon(y_te, pred)
        row = {"model": model.name, "rmse_all": round(rmse(y_te, pred), 2)}
        for h in horizons:
            row[f"rmse_{h}m"] = round(float(per_h[h // sm - 1]), 2)
        rows.append(row)

    res = pd.DataFrame(rows)
    print(res.to_string(index=False))
    return res


if __name__ == "__main__":
    main()
