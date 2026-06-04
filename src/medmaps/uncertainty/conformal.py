"""Calibrated prediction intervals.

Split conformal gives a finite-sample coverage guarantee, but only under
exchangeability, which a glucose stream violates. Adaptive Conformal Inference
(Gibbs and Candes, 2021) fixes this online: it nudges the working miscoverage level
up or down as it sees whether recent intervals actually covered, so long-run coverage
tracks the target even under drift. Both are here so the repo can show the textbook
version losing coverage and the adaptive one holding it.
"""

from __future__ import annotations

import numpy as np


def conformity_scores(y_true: np.ndarray, y_pred: np.ndarray) -> np.ndarray:
    """Absolute residuals, the nonconformity score for a regression forecast."""
    return np.abs(np.asarray(y_true) - np.asarray(y_pred))


def split_conformal_width(cal_scores: np.ndarray, alpha: float) -> float:
    """Half-width of a (1 - alpha) split-conformal interval from calibration scores.

    Uses the finite-sample corrected quantile level ceil((n+1)(1-alpha)) / n.
    """
    scores = np.asarray(cal_scores, dtype=float)
    n = len(scores)
    level = np.ceil((n + 1) * (1.0 - alpha)) / n
    level = float(min(level, 1.0))
    return float(np.quantile(scores, level))


def empirical_coverage(y_true: np.ndarray, lower: np.ndarray, upper: np.ndarray) -> float:
    """Fraction of points whose truth falls inside the interval."""
    y_true = np.asarray(y_true)
    return float(np.mean((y_true >= np.asarray(lower)) & (y_true <= np.asarray(upper))))


def adaptive_conformal(
    cal_scores: np.ndarray,
    y_true: np.ndarray,
    y_pred: np.ndarray,
    alpha: float,
    gamma: float = 0.01,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """ACI over a test stream processed in order.

    Returns (lower, upper, working_alpha). At each step the half-width is the
    split-conformal width at the current working level, the interval is
    pred +/- width, and the working level is updated by gamma * (alpha - miss),
    where miss is 1 when the truth fell outside.
    """
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    n = len(y_pred)
    lower = np.empty(n)
    upper = np.empty(n)
    working = np.empty(n)

    a = float(alpha)
    for t in range(n):
        a_clipped = min(max(a, 1e-3), 0.999)
        width = split_conformal_width(cal_scores, a_clipped)
        lo = y_pred[t] - width
        up = y_pred[t] + width
        lower[t] = lo
        upper[t] = up
        working[t] = a
        miss = 0.0 if (y_true[t] >= lo and y_true[t] <= up) else 1.0
        a = a + gamma * (alpha - miss)
    return lower, upper, working
