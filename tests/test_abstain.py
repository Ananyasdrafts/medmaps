"""Abstention tests. Pure numpy, runs in CI."""

import numpy as np

from medmaps.uncertainty.abstain import (
    abstain_by_ood,
    abstain_by_width,
    ood_scores,
    ood_threshold,
)


def test_abstain_by_width_flags_wide_intervals():
    lo = np.array([0.0, 0.0, 0.0])
    up = np.array([10.0, 50.0, 100.0])
    mask = abstain_by_width(lo, up, max_width=40.0)
    assert mask.tolist() == [False, True, True]


def test_ood_flags_shifted_inputs():
    rng = np.random.default_rng(0)
    x_train = rng.normal(100, 5, size=(200, 12, 3))  # in-distribution windows
    x_far = rng.normal(180, 5, size=(20, 12, 3))      # clearly shifted
    thr = ood_threshold(x_train, percentile=99.0)
    in_dist = abstain_by_ood(ood_scores(x_train, x_train), thr)
    shifted = abstain_by_ood(ood_scores(x_train, x_far), thr)
    assert in_dist.mean() <= 0.05    # almost never abstains on its own data
    assert shifted.all()             # always abstains on the shifted batch
