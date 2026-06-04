"""A faithfulness check for feature attributions.

The honest question about any explanation: if a feature really drove the prediction,
removing it should move the prediction accordingly. This ablates each feature (sets it
to its average) and correlates the claimed attribution with the actual change. A
glass-box model scores near 1 by construction; a method that only looks plausible will
not.
"""

from __future__ import annotations

from typing import Callable

import numpy as np


def ablation_faithfulness(
    predict_fn: Callable[[np.ndarray], np.ndarray],
    feats: np.ndarray,
    attributions: np.ndarray,
) -> float:
    """Correlation between claimed attributions and measured ablation effects.

    predict_fn maps a feature matrix to scalar predictions. For each feature, we set it
    to its training-mean value and record how much the prediction drops. A faithful
    positive attribution should match the drop caused by removing that feature.
    """
    feats = np.asarray(feats, dtype=float)
    base = predict_fn(feats)
    feat_mean = feats.mean(axis=0)
    effects = np.empty_like(attributions, dtype=float)
    for i in range(feats.shape[1]):
        ablated = feats.copy()
        ablated[:, i] = feat_mean[i]
        effects[:, i] = base - predict_fn(ablated)  # how much feature i was adding
    return float(np.corrcoef(attributions.ravel(), effects.ravel())[0, 1])
