"""Models: the race.

Every model implements the same interface and is judged on the same split, so the
evaluation report can name the real winner instead of assuming the deep model wins:

    naive_trend   linear extrapolation of recent slope (the baseline to beat)
    ridge_lagged  ridge regression on lagged features (a strong, honest baseline)
    tcn           temporal convolutional network
    gru           gated recurrent network
    nhits         N-HiTS, a hierarchical interpolation forecaster

Each produces a distributional forecast (quantiles), not a point, so event risk is
the predicted mass past the hypo/hyper threshold.
"""
