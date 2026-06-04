"""Forecaster base class.

Every model in the race implements `_fit` and `predict` (a median trajectory).
Quantiles come, for now, from the empirical distribution of training residuals per
horizon step. That is a deliberately simple, honest uncertainty baseline; the real
calibrated intervals arrive later from the uncertainty module (ACI / EnbPI).
"""

from __future__ import annotations

import numpy as np


class Forecaster:
    name = "base"

    def __init__(self) -> None:
        self._resid: np.ndarray | None = None

    def fit(self, X: np.ndarray, y: np.ndarray) -> "Forecaster":
        self._fit(X, y)
        self._resid = y - self.predict(X)
        return self

    def _fit(self, X: np.ndarray, y: np.ndarray) -> None:
        raise NotImplementedError

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Median trajectory, shape (n, horizon)."""
        raise NotImplementedError

    def predict_quantiles(self, X: np.ndarray, quantiles: list[float]) -> np.ndarray:
        """Return shape (n, horizon, n_quantiles)."""
        if self._resid is None:
            raise RuntimeError("call fit before predict_quantiles")
        point = self.predict(X)
        offsets = np.quantile(self._resid, quantiles, axis=0)  # (n_q, horizon)
        return point[:, :, None] + np.transpose(offsets)[None, :, :]
