"""Windowing tests. Pure-numpy/pandas, no simglucose, so these run in CI."""

import numpy as np
import pandas as pd

from medmaps.data.windowing import make_windows, temporal_split, windows_by_patient

FEATURES = ["cgm", "cho", "bolus", "basal"]


def _synthetic_patient(name: str, n: int = 100) -> pd.DataFrame:
    times = pd.date_range("2024-01-01", periods=n, freq="5min")
    cgm = 120 + 40 * np.sin(np.linspace(0, 6, n))  # oscillates ~80..160, no events
    cgm[50:55] = 60.0  # a deliberate hypo so an event label must fire
    return pd.DataFrame(
        {"time": times, "cgm": cgm, "cho": 0.0, "bolus": 0.0, "basal": 0.01, "patient": name}
    )


def test_make_windows_shapes_and_event():
    df = _synthetic_patient("p1", n=100)
    x, y, e = make_windows(df, input_steps=12, horizon_steps=6, feature_cols=FEATURES)
    assert x.shape == (100 - 18 + 1, 12, 4)
    assert y.shape == (100 - 18 + 1, 6)
    assert set(np.unique(e)).issubset({0, 1})
    assert e.sum() > 0  # the injected hypo must be caught by some window


def test_temporal_split_is_ordered():
    df = _synthetic_patient("p1", n=100)
    tr, te = temporal_split(df, train_frac=0.7)
    assert len(tr) == 70 and len(te) == 30
    assert tr["time"].max() < te["time"].min()  # no time overlap == no leakage


def test_windows_by_patient_counts():
    cohort = pd.concat([_synthetic_patient("p1"), _synthetic_patient("p2")], ignore_index=True)
    out = windows_by_patient(cohort, input_steps=12, horizon_steps=6, feature_cols=FEATURES)
    # per patient: train 70 -> 53 windows, test 30 -> 13 windows; two patients
    assert out["X_train"].shape[0] == 106
    assert out["X_test"].shape[0] == 26
    assert out["X_train"].shape[1:] == (12, 4)
