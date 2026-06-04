"""Abstention: when to say "not enough signal" instead of guessing.

Two reasons to stay quiet:
  - the calibrated interval is too wide to be actionable, or
  - the input looks unlike anything seen in training (out of distribution).

Both return a boolean mask where True means abstain.
"""

from __future__ import annotations

import numpy as np


def abstain_by_width(lower: np.ndarray, upper: np.ndarray, max_width: float) -> np.ndarray:
    """Abstain where the interval is wider than max_width (mg/dL)."""
    return (np.asarray(upper) - np.asarray(lower)) > max_width


def ood_scores(x_train: np.ndarray, x: np.ndarray) -> np.ndarray:
    """RMS standardized distance of each window to the training distribution.

    Windows are summarised by their per-feature mean over time, then scored by how
    many standard deviations (averaged over features) they sit from the training mean.
    """
    a_train = np.asarray(x_train, dtype=float).mean(axis=1)  # (n, n_features)
    a = np.asarray(x, dtype=float).mean(axis=1)
    mu = a_train.mean(axis=0)
    sd = a_train.std(axis=0) + 1e-6
    z = (a - mu) / sd
    return np.sqrt((z**2).mean(axis=1))


def ood_threshold(x_train: np.ndarray, percentile: float = 99.0) -> float:
    """Threshold = a high percentile of in-training OOD scores."""
    return float(np.percentile(ood_scores(x_train, x_train), percentile))


def abstain_by_ood(scores: np.ndarray, threshold: float) -> np.ndarray:
    """Abstain where the OOD score exceeds the threshold."""
    return np.asarray(scores) > threshold
