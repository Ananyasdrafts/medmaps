"""MedMaps: a glucose early-warning model that forecasts risk, explains it, and
abstains when it isn't sure.

Package layout:
    data/         generate CGM traces (simglucose), inject medication adherence,
                  window into supervised examples
    models/       the model race: naive trend, ridge-on-lags, TCN, GRU, N-HiTS
    uncertainty/  time-series-aware calibration (ACI / EnbPI) and abstention
    explain/      honest explanations (glass-box features + attribution + faithfulness)
    eval/         clinical evaluation (error grid, event lead-time, calibration, ...)
    api/          FastAPI serving layer
"""

__version__ = "0.1.0"
