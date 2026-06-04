# Evaluation report

Filled in as phase 1 produces results. Every number here is reproducible from
`configs/default.yaml`.

## setup

- data: simglucose cohort (see config)
- split: temporal, no leakage across the prediction window
- horizons: 30 and 60 minutes

## the model race

| model | RMSE (30m) | RMSE (60m) | error-grid A+B % | event sensitivity | notes |
|-------|-----------|-----------|------------------|-------------------|-------|
| naive_trend | | | | | baseline |
| ridge_lagged | | | | | |
| tcn | | | | | |
| gru | | | | | |
| nhits | | | | | |

## calibration and abstention

- target coverage vs empirical coverage (ACI):
- abstention trade-off curve (accuracy gained per unit of "I don't know"):
- vanilla split conformal vs ACI under shift (the failure demo):

## clinical view

- Clarke / Parkes error grid:
- event lead-time distribution:
- false-alarm rate at the chosen operating point:

## drift watch

- time-in-range trend detection:
- change-point examples:

## findings

(headline observations, mirrored into the README)
