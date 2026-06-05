"""Drift-watch tests. Pure numpy, runs in CI."""

import numpy as np

from medmaps.drift import detect_drift, glycemic_metrics


def test_metrics_on_in_range_series():
    m = glycemic_metrics(np.full(100, 120.0))
    assert m["time_in_range"] == 100.0
    assert m["time_below"] == 0.0 and m["time_above"] == 0.0


def test_metrics_count_lows_and_highs():
    cgm = np.array([60.0] * 25 + [120.0] * 50 + [200.0] * 25)
    m = glycemic_metrics(cgm)
    assert m["time_below"] == 25.0
    assert m["time_above"] == 25.0
    assert m["time_in_range"] == 50.0


def test_detect_drift_flags_worsening_control():
    rng = np.random.default_rng(0)
    baseline = rng.normal(120, 10, 500)              # mostly in range
    recent = np.concatenate([rng.normal(120, 10, 250), np.full(250, 210.0)])  # drifting high
    out = detect_drift(np.concatenate([baseline, recent]))
    assert out["status"] == "slipping"
    assert out["tir_delta"] < 0
    assert out["reasons"]


def test_detect_drift_stable_when_unchanged():
    rng = np.random.default_rng(1)
    cgm = rng.normal(120, 8, 1000)  # steady, in range throughout
    assert detect_drift(cgm)["status"] == "stable"
