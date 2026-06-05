"""Turn a per-patient time series into supervised windows, without leakage.

A window is (history -> future): `input_steps` of recent features predict the next
`horizon_steps` of glucose. Each window also carries a binary event label (does a
hypo or hyper occur anywhere in the future window), which the distributional
forecast is later scored against.

Splitting is strictly temporal and done per patient before windowing, so no window
ever straddles the train/test boundary.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def temporal_split(df: pd.DataFrame, train_frac: float = 0.7) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Split one patient's frame by time. Earlier portion trains, later tests."""
    cut = int(len(df) * train_frac)
    return df.iloc[:cut].copy(), df.iloc[cut:].copy()


def make_windows(
    df: pd.DataFrame,
    input_steps: int,
    horizon_steps: int,
    feature_cols: list[str],
    target_col: str = "cgm",
    thresholds: tuple[float, float] = (70.0, 180.0),
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Build (X, y, event) arrays from a single contiguous, time-sorted frame.

    X: (n, input_steps, n_features)  history
    y: (n, horizon_steps)            future glucose trajectory
    event: (n,)                      1 if a hypo/hyper occurs in the future window
    """
    feats = df[feature_cols].to_numpy(dtype=float)
    target = df[target_col].to_numpy(dtype=float)
    lo, hi = thresholds

    span = input_steps + horizon_steps
    n = len(df) - span + 1
    if n <= 0:
        empty_x = np.empty((0, input_steps, len(feature_cols)))
        return empty_x, np.empty((0, horizon_steps)), np.empty((0,), dtype=int)

    xs, ys, events = [], [], []
    for i in range(n):
        hist = feats[i : i + input_steps]
        future = target[i + input_steps : i + span]
        xs.append(hist)
        ys.append(future)
        events.append(int(future.min() < lo or future.max() > hi))

    return np.asarray(xs), np.asarray(ys), np.asarray(events, dtype=int)


def windows_by_patient(
    cohort: pd.DataFrame,
    input_steps: int,
    horizon_steps: int,
    feature_cols: list[str],
    train_frac: float = 0.7,
    **kwargs,
) -> dict[str, np.ndarray]:
    """Split each patient temporally, window both halves, and concatenate.

    Returns a dict with X_train, y_train, e_train, X_test, y_test, e_test.
    """
    keys = ("X_train", "y_train", "e_train", "X_test", "y_test", "e_test")
    parts: dict[str, list[np.ndarray]] = {k: [] for k in keys}

    for _, g in cohort.groupby("patient", sort=False):
        g = g.sort_values("time")
        tr, te = temporal_split(g, train_frac)
        for split, frame in (("train", tr), ("test", te)):
            x, y, e = make_windows(frame, input_steps, horizon_steps, feature_cols, **kwargs)
            parts[f"X_{split}"].append(x)
            parts[f"y_{split}"].append(y)
            parts[f"e_{split}"].append(e)

    return {k: np.concatenate(v) if v else np.empty((0,)) for k, v in parts.items()}
