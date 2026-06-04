"""Metric tests. Pure numpy, runs in CI."""

import numpy as np

from medmaps.eval.metrics import mae, rmse, rmse_per_horizon


def test_perfect_prediction_is_zero_error():
    y = np.array([[100.0, 110.0], [90.0, 95.0]])
    assert rmse(y, y) == 0.0
    assert mae(y, y) == 0.0


def test_known_values():
    y_true = np.array([[0.0, 0.0]])
    y_pred = np.array([[3.0, 4.0]])
    assert rmse(y_true, y_pred) == np.sqrt((9 + 16) / 2)
    assert mae(y_true, y_pred) == 3.5


def test_rmse_per_horizon_shape():
    y_true = np.zeros((5, 4))
    y_pred = np.ones((5, 4))
    out = rmse_per_horizon(y_true, y_pred)
    assert out.shape == (4,)
    assert np.allclose(out, 1.0)
