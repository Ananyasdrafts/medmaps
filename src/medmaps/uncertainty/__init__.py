"""Uncertainty and abstention.

Calibration uses time-series-aware conformal methods, because glucose data is
dependent and non-stationary and textbook split conformal silently loses its
coverage guarantee on it:

    aci    Adaptive Conformal Inference (Gibbs & Candes, 2021)
    enbpi  Ensemble batch Prediction Intervals (Xu & Xie, 2021)

Abstention fires when the calibrated interval is too wide to be actionable, or when
an out-of-distribution check says the input is unlike anything seen in training.
The "say when you don't know" guarantee is the core of the project.
"""
