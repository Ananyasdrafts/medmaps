"""Feature-engineering tests. Pure numpy, runs in CI."""

import numpy as np

from medmaps.explain.features import FEATURE_NAMES, engineer_window_features

COLS = ["cgm", "cho", "bolus", "basal"]


def _window(cgm, cho=None, bolus=None, basal=None):
    steps = len(cgm)
    cho = np.zeros(steps) if cho is None else np.asarray(cho)
    bolus = np.zeros(steps) if bolus is None else np.asarray(bolus)
    basal = np.zeros(steps) if basal is None else np.asarray(basal)
    return np.stack([cgm, cho, bolus, basal], axis=1)[None, ...]  # (1, steps, 4)


def test_shapes_and_names():
    x = _window(np.arange(12, dtype=float))
    feats, names = engineer_window_features(x, COLS)
    assert feats.shape == (1, len(FEATURE_NAMES))
    assert names == FEATURE_NAMES


def test_readable_feature_values():
    cgm = np.array([100, 102, 104, 106, 108, 110, 112, 114], dtype=float)  # rising
    x = _window(cgm, bolus=[0, 0, 0, 1, 0, 0, 0, 0])
    feats, names = engineer_window_features(x, COLS)
    f = dict(zip(names, feats[0]))
    assert f["last_cgm"] == 114
    assert f["slope_long"] > 0  # clearly trending up
    assert f["steps_since_bolus"] == 4  # bolus at index 3, window length 8
