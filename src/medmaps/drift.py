"""Slow-drift watch: the "your control is slipping" lens.

Acute alerts answer "what happens in the next hour." This answers the slower question
the market ignores: is this person's control quietly getting worse over days? It
summarises a stretch of CGM with the standard glycemic metrics (time in range,
variability, time low/high) and compares a recent window against an earlier baseline,
so a gradual decline shows up before any single reading looks alarming.
"""

from __future__ import annotations

import numpy as np

LOW = 70.0
HIGH = 180.0
CV_UNSTABLE = 0.36  # coefficient of variation above this is considered unstable control
TIR_DROP = 10.0  # a drop this many points in time-in-range counts as slipping


def glycemic_metrics(cgm, low: float = LOW, high: float = HIGH) -> dict:
    """Standard CGM summary for a stretch of readings."""
    cgm = np.asarray(cgm, dtype=float)
    mean = float(cgm.mean())
    sd = float(cgm.std())
    return {
        "time_in_range": round(100.0 * float(np.mean((cgm >= low) & (cgm <= high))), 1),
        "time_below": round(100.0 * float(np.mean(cgm < low)), 1),
        "time_above": round(100.0 * float(np.mean(cgm > high)), 1),
        "mean": round(mean, 1),
        "cv": round(sd / mean, 3) if mean else float("nan"),
    }


def detect_drift(
    cgm,
    baseline_frac: float = 0.5,
    low: float = LOW,
    high: float = HIGH,
    tir_drop: float = TIR_DROP,
    cv_unstable: float = CV_UNSTABLE,
) -> dict:
    """Compare a recent window of CGM against an earlier baseline and flag slipping."""
    cgm = np.asarray(cgm, dtype=float)
    cut = int(len(cgm) * baseline_frac)
    base = glycemic_metrics(cgm[:cut], low, high)
    recent = glycemic_metrics(cgm[cut:], low, high)

    reasons = []
    tir_delta = round(recent["time_in_range"] - base["time_in_range"], 1)
    if tir_delta <= -tir_drop:
        reasons.append(f"time in range fell {abs(tir_delta)} points")
    if recent["cv"] >= cv_unstable and recent["cv"] > base["cv"]:
        reasons.append(f"glucose swings widened (CV {recent['cv']})")
    if recent["time_below"] > base["time_below"] + 5:
        reasons.append(f"more time spent low ({recent['time_below']}%)")

    if reasons:
        status = "slipping"
    elif tir_delta >= tir_drop:
        status = "improving"
    else:
        status = "stable"

    return {
        "status": status,
        "tir_delta": tir_delta,
        "baseline": base,
        "recent": recent,
        "reasons": reasons,
    }
