"""The serving brain: one object that holds the trained glass-box, the conformal
calibration, and the OOD threshold, and turns a window of readings into a forecast,
an interval, a plain-language why, and an honest abstain decision.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from medmaps.config import load_config
from medmaps.data.simulate import simulate_cohort
from medmaps.data.windowing import windows_by_patient
from medmaps.explain.glassbox import GlassBoxForecaster
from medmaps.uncertainty.abstain import ood_scores, ood_threshold
from medmaps.uncertainty.conformal import conformity_scores, split_conformal_width

FEATURES = ["cgm", "cho", "bolus", "basal"]
_CACHE = Path("data/race_cohort.pkl")


def load_cohort(cfg: dict) -> pd.DataFrame:
    """Use the cached cohort if present, otherwise simulate a small one."""
    if _CACHE.exists():
        return pd.read_pickle(_CACHE)
    names = ["adolescent#001", "adult#001", "child#001"]
    df = simulate_cohort(names, 4, cfg["data"]["sample_minutes"], missed_bolus_prob=0.1,
                         seed=cfg["seed"])
    _CACHE.parent.mkdir(parents=True, exist_ok=True)
    df.to_pickle(_CACHE)
    return df


class MedMapsService:
    def __init__(self, cohort: pd.DataFrame | None = None, cfg: dict | None = None) -> None:
        self.cfg = cfg or load_config()
        self.sm = self.cfg["data"]["sample_minutes"]
        self.input_steps = self.cfg["task"]["input_window_minutes"] // self.sm
        self.horizon_steps = max(self.cfg["task"]["horizons_minutes"]) // self.sm
        self.horizons = self.cfg["task"]["horizons_minutes"]
        self.idx30 = 30 // self.sm - 1
        self.alpha = 1.0 - self.cfg["uncertainty"]["target_coverage"]
        self.max_width = self.cfg["abstention"]["max_interval_width"]
        self.hypo = self.cfg["task"]["thresholds"]["hypo"]
        self.hyper = self.cfg["task"]["thresholds"]["hyper"]
        self._rng = np.random.default_rng(self.cfg["seed"])
        self._fit(cohort if cohort is not None else load_cohort(self.cfg))

    def _fit(self, cohort: pd.DataFrame) -> None:
        data = windows_by_patient(cohort, self.input_steps, self.horizon_steps, FEATURES, 0.7)
        x_tr, y_tr = data["X_train"], data["y_train"]
        self.model = GlassBoxForecaster(FEATURES, alpha=1.0).fit(x_tr, y_tr)
        self._x_train = x_tr
        self._cal = conformity_scores(y_tr[:, self.idx30], self.model.predict(x_tr)[:, self.idx30])
        self._width = split_conformal_width(self._cal, self.alpha)
        self._ood_thr = ood_threshold(x_tr, percentile=99.0)
        self._test = (data["X_test"], data["y_test"], data["e_test"])

    def predict_window(self, window: list[list[float]]) -> dict:
        x = np.asarray(window, dtype=float)[None, ...]
        traj = self.model.predict(x)[0]
        lower, upper = traj - self._width, traj + self._width

        contribs, names = self.model.explain(x, self.idx30)
        order = np.argsort(-np.abs(contribs[0]))[:3]
        drivers = [
            {"feature": names[i], "contribution": round(float(contribs[0, i]), 1)} for i in order
        ]

        width30 = float(upper[self.idx30] - lower[self.idx30])
        ood = float(ood_scores(self._x_train, x)[0])
        too_wide = width30 > self.max_width
        out_of_dist = ood > self._ood_thr
        abstain = bool(too_wide or out_of_dist)
        reason = None
        if abstain:
            reason = "interval too wide to act on" if too_wide else "input unlike training data"

        risk = []
        for h in self.horizons:
            hi = h // self.sm - 1
            risk.append(
                {
                    "horizon_min": h,
                    "pred": round(float(traj[hi]), 1),
                    "lower": round(float(lower[hi]), 1),
                    "upper": round(float(upper[hi]), 1),
                    "event": bool(lower[hi] < self.hypo or upper[hi] > self.hyper),
                }
            )

        return {
            "horizon_minutes": [(i + 1) * self.sm for i in range(self.horizon_steps)],
            "forecast": [round(float(v), 1) for v in traj],
            "lower": [round(float(v), 1) for v in lower],
            "upper": [round(float(v), 1) for v in upper],
            "risk": risk,
            "drivers": drivers,
            "abstain": abstain,
            "reason": reason,
            "thresholds": {"hypo": self.hypo, "hyper": self.hyper},
        }

    def sample_window(
        self, index: int | None = None, event: bool = False, ood: bool = False
    ) -> dict:
        x_te, y_te, e_te = self._test
        pool = np.where(e_te == 1)[0] if event and (e_te == 1).any() else np.arange(len(x_te))
        i = int(pool[index % len(pool)]) if index is not None else int(self._rng.choice(pool))
        window = x_te[i].copy()
        ci = FEATURES.index("cgm")
        # an unfamiliar reading: shove glucose far outside the training range so the
        # OOD check fires and the model abstains. The true future is meaningless here.
        if ood:
            window[:, ci] = window[:, ci] + 300.0
        return {
            "index": i,
            "window": window.tolist(),
            "history_minutes": [(-(self.input_steps - 1 - k)) * self.sm for k in range(self.input_steps)],
            "history_cgm": [round(float(v), 1) for v in window[:, ci]],
            "true_future": None if ood else [round(float(v), 1) for v in y_te[i]],
        }
