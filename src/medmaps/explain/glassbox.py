"""An interpretable-by-design forecaster.

A linear model on the human-readable features. Its prediction decomposes exactly into
signed per-feature contributions, so every forecast comes with a truthful "what drove
this" instead of a post-hoc guess. It also joins the race, to check that being
explainable does not cost much accuracy.
"""

from __future__ import annotations

import numpy as np

from medmaps.explain.features import engineer_window_features
from medmaps.models.base import Forecaster


class GlassBoxForecaster(Forecaster):
    name = "glassbox"

    def __init__(self, feature_cols: list[str], alpha: float = 1.0) -> None:
        super().__init__()
        self.feature_cols = feature_cols
        self.alpha = alpha
        self._model = None
        self._names: list[str] | None = None
        self._feat_mean: np.ndarray | None = None

    def _features(self, X: np.ndarray) -> np.ndarray:
        feats, self._names = engineer_window_features(X, self.feature_cols)
        return feats

    def _fit(self, X: np.ndarray, y: np.ndarray) -> None:
        from sklearn.linear_model import Ridge

        feats = self._features(X)
        self._feat_mean = feats.mean(axis=0)
        self._model = Ridge(alpha=self.alpha).fit(feats, y)

    def predict(self, X: np.ndarray) -> np.ndarray:
        return self._model.predict(self._features(X))

    def explain(self, X: np.ndarray, horizon_step: int) -> tuple[np.ndarray, list[str]]:
        """Signed contribution of each feature to the prediction at one horizon step.

        contribution_i = coef_i * (feature_i - training_mean_i). These sum to the
        prediction minus its value at the average input, so they say how each feature
        pushed this particular call away from typical.
        """
        feats = self._features(X)
        coef = self._model.coef_[horizon_step]
        return coef * (feats - self._feat_mean), list(self._names)

    def predict_features(self, feats: np.ndarray, horizon_step: int) -> np.ndarray:
        """Predict directly from an engineered-feature matrix (used by faithfulness)."""
        return self._model.predict(feats)[:, horizon_step]
