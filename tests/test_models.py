"""Model tests. NaiveTrend and metrics are numpy-only (CI). Ridge is skipped
where scikit-learn isn't installed."""

import numpy as np
import pandas as pd

from medmaps.data.windowing import make_windows
from medmaps.eval.metrics import rmse
from medmaps.models.baselines import NaiveTrend

FEATURES = ["cgm", "cho"]


def _windows_from_series(cgm: np.ndarray, input_steps=8, horizon=4):
    df = pd.DataFrame(
        {
            "time": pd.date_range("2024-01-01", periods=len(cgm), freq="5min"),
            "cgm": cgm,
            "cho": 0.0,
        }
    )
    return make_windows(df, input_steps, horizon, FEATURES)


def test_naive_trend_nails_a_straight_line():
    # a perfectly linear series: extrapolating the slope should be near exact
    x, y, _ = _windows_from_series(2.0 * np.arange(60))
    model = NaiveTrend(target_index=0).fit(x, y)
    assert rmse(y, model.predict(x)) < 1e-6


def test_persistence_holds_last_value():
    from medmaps.models.baselines import NaivePersistence

    x, y, _ = _windows_from_series(np.full(60, 100.0))  # flat series -> exact
    model = NaivePersistence(target_index=0).fit(x, y)
    preds = model.predict(x)
    assert preds.shape == y.shape
    assert rmse(y, preds) == 0.0


def test_quantiles_are_shaped_and_monotone():
    rng = np.random.default_rng(0)
    cgm = 2.0 * np.arange(60) + rng.normal(0, 3, 60)  # noisy -> nonzero residuals
    x, y, _ = _windows_from_series(cgm)
    model = NaiveTrend(target_index=0).fit(x, y)
    q = model.predict_quantiles(x, [0.1, 0.5, 0.9])
    assert q.shape == (x.shape[0], 4, 3)
    # quantiles must not decrease across the quantile axis
    assert np.all(np.diff(q, axis=-1) >= -1e-9)


def test_ridge_runs_and_predicts():
    import pytest

    pytest.importorskip("sklearn")
    from medmaps.models.baselines import RidgeLagged

    x, y, _ = _windows_from_series(2.0 * np.arange(80))
    model = RidgeLagged(alpha=1.0).fit(x, y)
    preds = model.predict(x)
    assert preds.shape == y.shape
    assert np.isfinite(rmse(y, preds))
