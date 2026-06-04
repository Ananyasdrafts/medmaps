"""Forecast metrics. Clinical metrics (error grid, event lead-time, calibration)
are added as the evaluation phase fills out; these are the regression basics."""

from __future__ import annotations

import numpy as np


def rmse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    return float(np.sqrt(np.mean((y_true - y_pred) ** 2)))


def mae(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    return float(np.mean(np.abs(y_true - y_pred)))


def rmse_per_horizon(y_true: np.ndarray, y_pred: np.ndarray) -> np.ndarray:
    """RMSE at each step of the forecast horizon, shape (horizon,)."""
    return np.sqrt(np.mean((y_true - y_pred) ** 2, axis=0))
