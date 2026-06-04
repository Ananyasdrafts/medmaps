"""Glass-box + faithfulness tests. Skipped where scikit-learn isn't installed."""

import numpy as np
import pandas as pd
import pytest

pytest.importorskip("sklearn")

from medmaps.data.windowing import make_windows  # noqa: E402
from medmaps.explain.faithfulness import ablation_faithfulness  # noqa: E402
from medmaps.explain.features import engineer_window_features  # noqa: E402
from medmaps.explain.glassbox import GlassBoxForecaster  # noqa: E402

COLS = ["cgm", "cho", "bolus", "basal"]


def _windows(n=200, input_steps=12, horizon=12):
    rng = np.random.default_rng(0)
    cgm = 120 + 30 * np.sin(np.linspace(0, 10, n)) + rng.normal(0, 2, n)
    df = pd.DataFrame(
        {
            "time": pd.date_range("2024-01-01", periods=n, freq="5min"),
            "cgm": cgm,
            "cho": 0.0,
            "bolus": 0.0,
            "basal": 0.01,
        }
    )
    return make_windows(df, input_steps, horizon, COLS)


def test_glassbox_predicts_and_explains_exactly():
    x, y, _ = _windows()
    gb = GlassBoxForecaster(COLS, alpha=1.0).fit(x, y)
    h = 5
    pred = gb.predict(x)[:, h]
    contribs, _ = gb.explain(x, h)
    baseline = gb._model.predict(gb._feat_mean[None, :])[0, h]
    # contributions must reconstruct the prediction (minus the average-input baseline)
    assert np.allclose(contribs.sum(axis=1), pred - baseline, atol=1e-6)


def test_glassbox_explanations_are_faithful():
    x, y, _ = _windows()
    gb = GlassBoxForecaster(COLS, alpha=1.0).fit(x, y)
    h = 5
    contribs, _ = gb.explain(x, h)
    feats = engineer_window_features(x, COLS)[0]
    faith = ablation_faithfulness(lambda f: gb.predict_features(f, h), feats, contribs)
    assert faith > 0.99  # glass-box is faithful by construction
