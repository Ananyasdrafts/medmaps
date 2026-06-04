"""Conformal tests. Pure numpy, runs in CI."""

import numpy as np

from medmaps.uncertainty.conformal import (
    adaptive_conformal,
    conformity_scores,
    empirical_coverage,
    split_conformal_width,
)


def test_split_conformal_hits_target_when_exchangeable():
    rng = np.random.default_rng(0)
    cal = np.abs(rng.standard_normal(4000))
    width = split_conformal_width(cal, alpha=0.1)
    test = np.abs(rng.standard_normal(4000))
    coverage = float(np.mean(test <= width))
    assert 0.86 <= coverage <= 0.94  # near the 0.90 promise on exchangeable data


def test_empirical_coverage_counts_inside():
    y = np.array([0.0, 5.0, 10.0])
    lo = np.array([-1.0, 4.0, 20.0])
    up = np.array([1.0, 6.0, 30.0])
    assert empirical_coverage(y, lo, up) == 2 / 3


def test_conformity_scores_are_absolute_residuals():
    assert np.allclose(conformity_scores([1.0, 2.0], [1.5, 0.0]), [0.5, 2.0])


def test_adaptive_conformal_tracks_target_and_is_bounded():
    rng = np.random.default_rng(1)
    cal = np.abs(rng.standard_normal(2000))
    pred = np.zeros(3000)
    true = rng.standard_normal(3000)  # residual == |true|, same family as cal
    lo, up, working = adaptive_conformal(cal, true, pred, alpha=0.1, gamma=0.01)
    assert lo.shape == up.shape == working.shape == (3000,)
    assert 0.0 <= working.min() and working.max() <= 1.0
    assert 0.85 <= empirical_coverage(true, lo, up) <= 0.95
