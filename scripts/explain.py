"""Explanation demo.

Fit the glass-box forecaster, check it stays competitive with ridge, show what drives
a few 30-minute calls in plain words, and measure whether those explanations are
faithful. Uses the cached race cohort. Run from the repo root:
    PYTHONPATH=src python scripts/explain.py
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from medmaps.config import load_config
from medmaps.data.windowing import windows_by_patient
from medmaps.eval.metrics import rmse_per_horizon
from medmaps.explain.faithfulness import ablation_faithfulness
from medmaps.explain.features import engineer_window_features
from medmaps.explain.glassbox import GlassBoxForecaster
from medmaps.models.baselines import RidgeLagged

FEATURES = ["cgm", "cho", "bolus", "basal"]
CACHE = Path("data/race_cohort.pkl")


def main() -> None:
    cfg = load_config()
    sm = cfg["data"]["sample_minutes"]
    input_steps = cfg["task"]["input_window_minutes"] // sm
    horizon_steps = max(cfg["task"]["horizons_minutes"]) // sm
    idx = 30 // sm - 1

    cohort = pd.read_pickle(CACHE)
    data = windows_by_patient(cohort, input_steps, horizon_steps, FEATURES, train_frac=0.7)
    x_tr, y_tr, x_te, y_te = data["X_train"], data["y_train"], data["X_test"], data["y_test"]

    glass = GlassBoxForecaster(FEATURES, alpha=1.0).fit(x_tr, y_tr)
    ridge = RidgeLagged(alpha=1.0).fit(x_tr, y_tr)
    g_rmse = rmse_per_horizon(y_te, glass.predict(x_te))
    r_rmse = rmse_per_horizon(y_te, ridge.predict(x_te))
    print("RMSE @30m / @60m (mg/dL)")
    print(f"  glassbox: {g_rmse[idx]:.2f} / {g_rmse[-1]:.2f}")
    print(f"  ridge   : {r_rmse[idx]:.2f} / {r_rmse[-1]:.2f}")

    contribs, names = glass.explain(x_te, idx)
    faith = ablation_faithfulness(
        lambda f: glass.predict_features(f, idx),
        engineer_window_features(x_te, FEATURES)[0],
        contribs,
    )
    print(f"\nexplanation faithfulness (1.0 = perfect): {faith:.3f}")

    print("\nwhy these 30-minute calls (top 3 drivers each):")
    pred = glass.predict(x_te)[:, idx]
    for s in range(3):
        order = np.argsort(-np.abs(contribs[s]))[:3]
        drivers = ", ".join(
            f"{names[i]} {'+' if contribs[s, i] >= 0 else '-'}{abs(contribs[s, i]):.1f}"
            for i in order
        )
        print(f"  pred {pred[s]:.0f} mg/dL  <-  {drivers}")


if __name__ == "__main__":
    main()
