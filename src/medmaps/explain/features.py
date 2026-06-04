"""Human-readable features from a recent window.

These are the things a clinician actually reasons about: where glucose is now, which
way it is moving and how fast, how variable it has been, and what insulin and carbs
just happened. A model built on these can explain itself in words instead of
gesturing at an attention map.
"""

from __future__ import annotations

import numpy as np

FEATURE_NAMES = [
    "last_cgm",
    "mean_cgm",
    "std_cgm",
    "range_cgm",
    "slope_short",
    "slope_long",
    "carbs_recent",
    "bolus_recent",
    "basal_mean",
    "steps_since_bolus",
]


def _slope(series: np.ndarray) -> np.ndarray:
    """Least-squares slope per row of a (n, k) array."""
    k = series.shape[1]
    t = np.arange(k, dtype=float)
    tc = t - t.mean()
    denom = (tc**2).sum()
    return ((series - series.mean(axis=1, keepdims=True)) * tc).sum(axis=1) / denom


def engineer_window_features(
    X: np.ndarray, feature_cols: list[str]
) -> tuple[np.ndarray, list[str]]:
    """Turn windows (n, steps, n_features) into (n, len(FEATURE_NAMES)) readable features."""
    ci = feature_cols.index("cgm")
    cgm = X[:, :, ci]
    cho = X[:, :, feature_cols.index("cho")]
    bolus = X[:, :, feature_cols.index("bolus")]
    basal = X[:, :, feature_cols.index("basal")]
    steps = cgm.shape[1]

    short = cgm[:, -3:] if steps >= 3 else cgm
    bolus_mask = bolus > 0
    last_bolus_idx = np.where(bolus_mask, np.arange(steps), -1).max(axis=1)
    steps_since_bolus = np.where(last_bolus_idx >= 0, (steps - 1) - last_bolus_idx, steps)

    feats = np.column_stack(
        [
            cgm[:, -1],
            cgm.mean(axis=1),
            cgm.std(axis=1),
            cgm.max(axis=1) - cgm.min(axis=1),
            _slope(short),
            _slope(cgm),
            cho.sum(axis=1),
            bolus.sum(axis=1),
            basal.mean(axis=1),
            steps_since_bolus.astype(float),
        ]
    )
    return feats, list(FEATURE_NAMES)
