"""The baselines that any deep model has to beat to earn its place.

NaiveTrend extrapolates the recent slope of glucose. RidgeLagged is linear
regression on the flattened recent window. On short-horizon CGM these are
notoriously strong, which is exactly why they go first.
"""

from __future__ import annotations

import numpy as np

from .base import Forecaster


class NaiveTrend(Forecaster):
    name = "naive_trend"

    def __init__(self, target_index: int = 0, slope_window: int = 6) -> None:
        super().__init__()
        self.target_index = target_index
        self.slope_window = slope_window
        self.horizon: int | None = None

    def _fit(self, X: np.ndarray, y: np.ndarray) -> None:
        self.horizon = int(y.shape[1])

    def predict(self, X: np.ndarray) -> np.ndarray:
        series = X[:, :, self.target_index]            # (n, input_steps)
        k = min(self.slope_window, series.shape[1])
        recent = series[:, -k:]
        t = np.arange(k, dtype=float)
        t_centered = t - t.mean()
        denom = (t_centered**2).sum()
        slope = (
            (recent - recent.mean(axis=1, keepdims=True)) * t_centered
        ).sum(axis=1) / denom
        last = series[:, -1]
        steps = np.arange(1, self.horizon + 1, dtype=float)
        return last[:, None] + slope[:, None] * steps[None, :]


class RidgeLagged(Forecaster):
    name = "ridge_lagged"

    def __init__(self, alpha: float = 1.0) -> None:
        super().__init__()
        self.alpha = alpha
        self._model = None

    def _fit(self, X: np.ndarray, y: np.ndarray) -> None:
        from sklearn.linear_model import Ridge

        self._model = Ridge(alpha=self.alpha)
        self._model.fit(self._flatten(X), y)

    def predict(self, X: np.ndarray) -> np.ndarray:
        return self._model.predict(self._flatten(X))

    @staticmethod
    def _flatten(X: np.ndarray) -> np.ndarray:
        return X.reshape(X.shape[0], -1)
