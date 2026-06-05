<!-- github.com/Ananyasdrafts/medmaps -->

# MedMaps

An early-warning layer for continuous glucose monitors. It predicts a high or low
before it happens, explains the call, and would rather warn you early than miss a low.

`status: phase 1 complete`

## demo

**[Try it live](https://ananyasdrafts.github.io/medmaps/)** (runs in the browser, no setup)

![MedMaps live monitor](docs/images/demo.gif)

The dashboard plays a glucose stream forward in time: the forecast and its uncertainty
band project ahead of "now," the alert fires *before* the event with its reason and a
phone-style notification, and a panel underneath tracks the slower "is control
slipping" picture. It is the engine's explainer view; the real product is a push
notification on a phone.

## results

A few findings worth the scroll. Full tables are in
[docs/eval-report.md](docs/eval-report.md); the story behind them is in
[docs/rebuild-notes.md](docs/rebuild-notes.md).

- **Simple beats deep.** In a head-to-head race, a glass-box linear model and plain
  persistence beat a GRU and a TCN at both the 30 and 60-minute horizons. The "simple
  is hard to beat on time series" result, in my own numbers.
- **The uncertainty is honest.** Calibrated on two patients and tested on a held-out
  third, textbook conformal silently drops to **63% coverage** against a 90% promise;
  Adaptive Conformal Inference recovers it to **85%**.
- **Interpretability was free.** The most accurate model is the glass-box one on 10
  human-readable features, and its explanations are faithful by construction (**0.977**
  on an ablation check), so every alert says why in plain terms, not an attention map.
- **It holds up clinically.** **~97%** of predictions land in the Clarke error grid's
  clinically-acceptable zones, and it catches **78%** of hypo/hyper events at a **1%**
  false-alarm rate.

## the sketch

People managing diabetes get a stream of glucose readings and almost no help reading
them. The dangerous moments, a low overnight or a slow loss of control over weeks, are
exactly the ones that go unnoticed until they are urgent. What sets MedMaps apart from
the threshold alerts already on the market:

- it **explains** every alert (falling fast, insulin still active, light on carbs),
- it **cuts false alarms with context** (recent carbs can cover a coming low, recent
  insulin can bring down a coming high) and flags an unreliable reading **out loud**
  ("check manually") rather than guessing or going silent,
- and it watches the **slow drift** no consumer CGM surfaces.

It is deliberately not balanced. In glucose care a missed low is far worse than a false
alarm, so the alert errs toward warning.

## how it works

Five rules, each there to avoid a way these systems usually fail:

1. **No assumed winner.** Naive trend, ridge on lagged features, a TCN, a GRU, and
   N-HiTS race on the same split. The repo reports who actually wins, even if it is the
   boring model.
2. **Predict a distribution, not a point.** Event risk is the predicted mass past the
   threshold, so uncertainty flows into the risk number instead of being bolted on.
3. **Time-series-aware uncertainty.** Calibration uses Adaptive Conformal Inference,
   not textbook split conformal, which silently loses its coverage guarantee on
   dependent, shifting data.
4. **Honest explanations.** No pretending attention weights are reasons. An
   interpretable-by-design model on human-readable features, with a faithfulness check.
5. **Clinical evaluation.** Clarke error grid, event lead-time and sensitivity, interval
   calibration, false-alarm rate. Not just RMSE.

## run it

Config-driven: the knobs live in [configs/default.yaml](configs/default.yaml).

```bash
python -m venv .venv
.venv\Scripts\activate                               # Windows (use source .venv/bin/activate elsewhere)
pip install -e .
PYTHONPATH=src python scripts/generate_cohort.py     # pre-build the demo cohort cache
PYTHONPATH=src uvicorn medmaps.api.app:app --port 8000
```

Dashboard, second terminal:

```bash
cd frontend && npm install && npm run dev            # opens on :5173
```

Reproduce the findings: `scripts/race.py`, `scripts/abstain.py`, `scripts/explain.py`,
`scripts/clinical.py` (each with `PYTHONPATH=src python ...`).

## limitations

The honest one, and the next milestone: **MedMaps is validated on simulated CGM, not
real patients yet.** v1 runs on [simglucose](https://github.com/jxx123/simglucose), the
FDA-accepted UVA/Padova simulator. That is a deliberate choice, it makes the whole repo
reproducible with no PHI and no data-access gatekeeping, so anyone can clone and run it.
But a simulator is smooth in ways real CGM is not (sensor noise, compression lows, human
messiness), and the cohort here is small and single-seed, so the numbers are a baseline
bar, not a verdict.

## roadmap

- phase 1 `done` : glucose early-warning end to end — model race, conformal abstention,
  glass-box explanations, clinical eval, safety-asymmetric alerts, drift watch, light
  personalization, live-monitor dashboard
- phase 2 `next` : **validate on real CGM data** ([OhioT1DM](http://smarthealth.cs.ohio.edu/OhioT1DM-dataset.html),
  the standard forecasting benchmark, then broader real-world data like OpenAPS and
  Tidepool/Open Humans), then a second vital and deeper personalization
