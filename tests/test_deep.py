"""Deep-model tests. Skipped where torch isn't installed (e.g. CI)."""

import numpy as np
import pandas as pd
import pytest

pytest.importorskip("torch")

from medmaps.data.windowing import make_windows  # noqa: E402
from medmaps.models.deep import GRUForecaster, TCNForecaster  # noqa: E402


def _windows(n=120, input_steps=8, horizon=4):
    cgm = 120 + 30 * np.sin(np.linspace(0, 8, n))
    df = pd.DataFrame(
        {"time": pd.date_range("2024-01-01", periods=n, freq="5min"), "cgm": cgm, "cho": 0.0}
    )
    return make_windows(df, input_steps, horizon, ["cgm", "cho"])


@pytest.mark.parametrize("model_cls", [GRUForecaster, TCNForecaster])
def test_deep_model_fits_and_predicts(model_cls):
    x, y, _ = _windows()
    model = model_cls(epochs=2).fit(x, y)  # tiny epoch count: shape/finiteness only
    preds = model.predict(x)
    assert preds.shape == y.shape
    assert np.isfinite(preds).all()
