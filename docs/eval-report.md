# Evaluation report

Filled in as phase 1 produces results. Every number here is reproducible from
`configs/default.yaml`.

## setup

- data: simglucose cohort, 3 patients x 4 days, single seed (small, preliminary)
- split: temporal 70/30 per patient, no leakage across the prediction window
- horizons: 30 and 60 minutes; RMSE in mg/dL

## the model race

| model | RMSE 30m | RMSE 60m | notes |
|-------|---------:|---------:|-------|
| naive_persistence | 23.66 | 36.14 | hold last value; the real baseline |
| naive_trend | 31.67 | 61.04 | slope extrapolation; overshoots long-horizon |
| ridge_lagged | **21.10** | 38.99 | ridge on flattened multivariate lags |
| tcn | pending | pending | |
| gru | pending | pending | |
| nhits | pending | pending | |

Clinical metrics (error grid, event lead-time, sensitivity) and calibrated
intervals are not in this table yet; RMSE only so far.

## findings (so far)

1. **Persistence is hard to beat at 30 min.** Holding the last reading flat scores
   23.66, only ~2.5 mg/dL behind the best model (ridge, 21.10). The trivial
   baseline is a real bar, consistent with the CGM literature.
2. **The ranking flips by 60 min.** Persistence (36.14) beats ridge (38.99) at the
   longer horizon. The "smarter" linear model loses to doing nothing once you look
   an hour ahead. Any deep model has to beat persistence at both horizons, and
   especially at 60 min, to justify its complexity.
3. **Slope extrapolation is the wrong naive.** naive_trend is worst at both horizons
   and overshoots badly at 60 min (61.04), because a straight-line slope diverges.
   Persistence, not trend, is the baseline to report against.
4. **The pipeline looks sound.** Ridge at ~21 mg/dL @30min sits in the range of
   published CGM forecasters, a sign the data and windowing are not producing
   nonsense.

Caveats: tiny cohort and a single seed, quantiles are residual-based not yet
conformally calibrated, and no hyperparameters were tuned. Treat as a baseline bar,
not a verdict.

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
