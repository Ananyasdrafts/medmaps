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
| ridge_lagged | 21.10 | 38.99 | ridge on flattened multivariate lags |
| gru | 30.09 | 44.34 | small + modestly trained here |
| tcn | 28.69 | 47.78 | small + modestly trained here |
| glassbox | **21.08** | **35.77** | interpretable-by-design; best overall |
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
5. **The deep models did not earn their complexity (here).** A GRU and a TCN,
   trained modestly, land at 28-30 mg/dL @30min and 44-48 @60min, behind both ridge
   and persistence at both horizons. This is the DLinear lesson in miniature: on
   limited time-series data, simple wins. It is not proof deep models cannot help;
   they are data-hungry and this cohort is small. But on equal footing today, the
   simple models win and the deep ones have to justify themselves.

6. **The interpretable model won.** A linear glass-box on 10 human-readable features
   (21.08 @30min, 35.77 @60min) matches ridge at 30 min and beats every model,
   including persistence, at 60 min. Interpretability cost nothing here; it was the
   most accurate model in the race.

Caveats: tiny cohort and a single seed, deep models trained modestly with no tuning,
quantiles are residual-based not yet conformally calibrated. Treat as a baseline bar,
not a verdict. The fair rematch is a much larger cohort with tuned deep models.

## explanations

The glass-box forecaster is interpretable by construction: each prediction decomposes
exactly into signed per-feature contributions, so the "what drove this" is the model
itself, not a post-hoc story. The ablation faithfulness check (claimed contributions
vs the measured effect of removing each feature) scores **0.977**. Attention weights
carry no such guarantee, which is why they are not used as the explanation.

Example 30-minute calls (top drivers, signed, mg/dL):

```text
pred 100  <-  last_cgm -10.6, slope_short -7.2, std_cgm +6.2
pred  99  <-  last_cgm -11.9, slope_short -6.1, carbs_recent -5.9
pred 101  <-  last_cgm -12.0, carbs_recent -5.9, std_cgm +4.5
```

## calibration and abstention

Setup: calibrate on two patients, test on a held-out third (a real cross-patient
shift), 30-minute horizon, target coverage 90%.

| method | empirical coverage | note |
|--------|-------------------:|------|
| split conformal (textbook) | 0.629 | collapses under shift |
| adaptive conformal (ACI) | 0.853 | recovers toward target |

- mean ACI interval width: 89 mg/dL, wide because the held-out patient is genuinely
  hard to predict from a model that never saw them
- with a 60 mg/dL actionability threshold the system abstains on 85% of calls; on the
  kept set ACI coverage is 0.836

This is the failure the project exists to avoid, shown on purpose. Textbook conformal
quietly drops to 63% coverage on a new patient while still claiming 90%; ACI adapts
its level online and climbs back toward target. The high abstention rate is the system
correctly refusing to make confident calls for someone unlike anyone it trained on.
Subtle but important: width-based abstention handles variance, not systematic bias, so
a model that is consistently off for a new population needs a broader cohort, not just
wider error bars. (Stress test: only two training patients and a deliberately
different test patient; abstention falls as the cohort grows.)

## clinical view

- Clarke / Parkes error grid:
- event lead-time distribution:
- false-alarm rate at the chosen operating point:

## drift watch

- time-in-range trend detection:
- change-point examples:

## findings

(headline observations, mirrored into the README)
