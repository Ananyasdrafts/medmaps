"""Abstention demo at the 30-minute horizon.

Calibrate on two patients, test on a held-out third (a real covariate shift), and
compare textbook split conformal against Adaptive Conformal Inference. Then apply the
abstain rule (too-wide interval or out-of-distribution input) and report coverage on
what is left. Uses the cached race cohort. Run from the repo root:
    PYTHONPATH=src python scripts/abstain.py
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from medmaps.config import load_config
from medmaps.data.windowing import make_windows, temporal_split
from medmaps.models.baselines import RidgeLagged
from medmaps.uncertainty.abstain import (
    abstain_by_ood,
    abstain_by_width,
    ood_scores,
    ood_threshold,
)
from medmaps.uncertainty.conformal import (
    adaptive_conformal,
    conformity_scores,
    empirical_coverage,
    split_conformal_width,
)

FEATURES = ["cgm", "cho", "bolus", "basal"]
TRAIN_PATIENTS = ["adolescent#001", "adult#001"]
TEST_PATIENT = "child#001"
CACHE = Path("data/race_cohort.pkl")


def _windows(g: pd.DataFrame, input_steps: int, horizon_steps: int):
    return make_windows(g.sort_values("time"), input_steps, horizon_steps, FEATURES)


def main() -> None:
    cfg = load_config()
    sm = cfg["data"]["sample_minutes"]
    input_steps = cfg["task"]["input_window_minutes"] // sm
    horizon_steps = max(cfg["task"]["horizons_minutes"]) // sm
    idx = 30 // sm - 1  # the 30-minute step
    alpha = 1.0 - cfg["uncertainty"]["target_coverage"]
    gamma = cfg["uncertainty"]["aci_step_size"]
    max_width = cfg["abstention"]["max_interval_width"]

    cohort = pd.read_pickle(CACHE)

    fit_x, fit_y, cal_x, cal_y = [], [], [], []
    for name in TRAIN_PATIENTS:
        g = cohort[cohort.patient == name]
        tr, ca = temporal_split(g, 0.7)
        xf, yf, _ = _windows(tr, input_steps, horizon_steps)
        xc, yc, _ = _windows(ca, input_steps, horizon_steps)
        fit_x.append(xf)
        fit_y.append(yf)
        cal_x.append(xc)
        cal_y.append(yc)
    x_fit, y_fit = np.concatenate(fit_x), np.concatenate(fit_y)
    x_cal, y_cal = np.concatenate(cal_x), np.concatenate(cal_y)
    x_te, y_te, _ = _windows(cohort[cohort.patient == TEST_PATIENT], input_steps, horizon_steps)

    model = RidgeLagged(alpha=1.0).fit(x_fit, y_fit)
    scores = conformity_scores(y_cal[:, idx], model.predict(x_cal)[:, idx])
    pred_te = model.predict(x_te)[:, idx]
    true_te = y_te[:, idx]

    # textbook split conformal: one fixed width
    w = split_conformal_width(scores, alpha)
    cov_split = empirical_coverage(true_te, pred_te - w, pred_te + w)

    # adaptive conformal
    lo, up, _ = adaptive_conformal(scores, true_te, pred_te, alpha, gamma)
    cov_aci = empirical_coverage(true_te, lo, up)

    # abstain: too-wide interval or out-of-distribution input
    keep = ~(
        abstain_by_width(lo, up, max_width)
        | abstain_by_ood(ood_scores(x_fit, x_te), ood_threshold(x_fit))
    )
    cov_kept = empirical_coverage(true_te[keep], lo[keep], up[keep]) if keep.any() else float("nan")

    print(f"target coverage              : {1 - alpha:.2f}")
    print(f"split conformal coverage     : {cov_split:.3f}")
    print(f"adaptive (ACI) coverage      : {cov_aci:.3f}")
    print(f"mean interval width (mg/dL)  : {(up - lo).mean():.1f}")
    print(f"abstention rate              : {1 - keep.mean():.1%}")
    print(f"ACI coverage on kept set     : {cov_kept:.3f}")


if __name__ == "__main__":
    main()
