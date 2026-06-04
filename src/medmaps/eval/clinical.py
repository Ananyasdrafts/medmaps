"""Clinical evaluation: the metrics a diabetes clinician would actually ask for.

RMSE treats every error the same. These do not. The Clarke error grid asks whether an
error is harmless or dangerous; event detection asks whether we catch the lows and
highs, and how early; the false-alarm rate asks how often we cry wolf, which is what
makes people switch an alarm off.
"""

from __future__ import annotations

import numpy as np

HYPO = 70.0
HYPER = 180.0


def clarke_zones(ref: np.ndarray, pred: np.ndarray) -> np.ndarray:
    """Classify each (reference, predicted) glucose pair into a Clarke zone A-E.

    Zone A/B are clinically acceptable; C/D/E are progressively dangerous. Boundaries
    follow the standard Clarke Error Grid Analysis.
    """
    ref = np.asarray(ref, dtype=float)
    pred = np.asarray(pred, dtype=float)

    zone_a = ((ref <= 70) & (pred <= 70)) | ((pred <= 1.2 * ref) & (pred >= 0.8 * ref))
    zone_e = ((ref >= 180) & (pred <= 70)) | ((ref <= 70) & (pred >= 180))
    zone_c = (((ref >= 70) & (ref <= 290)) & (pred >= ref + 110)) | (
        ((ref >= 130) & (ref <= 180)) & (pred <= (7.0 / 5.0) * ref - 182)
    )
    zone_d = (((ref >= 240) & (pred >= 70) & (pred <= 180))) | (
        ((ref <= 70) & (pred >= 70) & (pred <= 180))
    )
    # priority A > E > C > D, else B
    return np.select([zone_a, zone_e, zone_c, zone_d], ["A", "E", "C", "D"], default="B")


def zone_percentages(zones: np.ndarray) -> dict[str, float]:
    """Percent of points in each Clarke zone."""
    return {z: round(100.0 * float(np.mean(zones == z)), 2) for z in "ABCDE"}


def _events(traj: np.ndarray, hypo: float = HYPO, hyper: float = HYPER) -> np.ndarray:
    """Boolean per window: does a hypo or hyper occur anywhere in the trajectory."""
    traj = np.asarray(traj, dtype=float)
    return (traj.min(axis=1) < hypo) | (traj.max(axis=1) > hyper)


def event_detection(
    true_traj: np.ndarray, pred_traj: np.ndarray, hypo: float = HYPO, hyper: float = HYPER
) -> dict[str, float]:
    """Sensitivity, specificity, and false-alarm rate for catching hypo/hyper events."""
    yt = _events(true_traj, hypo, hyper)
    yp = _events(pred_traj, hypo, hyper)
    tp, fn = int((yt & yp).sum()), int((yt & ~yp).sum())
    fp, tn = int((~yt & yp).sum()), int((~yt & ~yp).sum())
    return {
        "sensitivity": tp / (tp + fn) if tp + fn else float("nan"),
        "specificity": tn / (tn + fp) if tn + fp else float("nan"),
        "false_alarm_rate": fp / (fp + tn) if fp + tn else float("nan"),
        "tp": tp, "fn": fn, "fp": fp, "tn": tn,
    }


def lead_times(
    true_traj: np.ndarray,
    pred_traj: np.ndarray,
    sample_minutes: int,
    hypo: float = HYPO,
    hyper: float = HYPER,
) -> np.ndarray:
    """Minutes of warning for each correctly caught event.

    For windows where a real event occurs and the model also predicts one, the lead
    time is when the real event first crosses a threshold inside the horizon.
    """
    true_traj = np.asarray(true_traj, dtype=float)
    caught = _events(true_traj, hypo, hyper) & _events(pred_traj, hypo, hyper)
    out = []
    for tr in true_traj[caught]:
        cross = np.where((tr < hypo) | (tr > hyper))[0]
        if len(cross):
            out.append((cross[0] + 1) * sample_minutes)
    return np.asarray(out, dtype=float)
