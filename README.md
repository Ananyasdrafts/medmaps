<!-- github.com/Ananyasdrafts/medmaps -->

# MedMaps

A glucose early-warning model that forecasts risk before an event, explains what
drove the call, and stays quiet when it isn't sure.

`status: building` · phase 1 of 4

## the sketch

People managing diabetes get a stream of glucose readings and almost no help
reading them. The dangerous moments, a low overnight, a slow loss of control over
weeks, are exactly the ones that go unnoticed until they are urgent.

MedMaps watches the stream on two timescales:

- **acute warning**: predicts an oncoming hypo (<70 mg/dL) or hyper (>180 mg/dL)
  event 30 to 60 minutes out, the window where you can still act.
- **drift watch**: a slower signal over hours and days that flags when control is
  quietly slipping, before any single reading looks alarming.

The point that matters most: when the signal is thin or unfamiliar, MedMaps says
"not enough to call this" instead of firing a confident wrong alert. A false alarm
costs trust, and a missed event costs more. The model is built to know the
difference.

## how it works

The design follows five rules, each there to avoid a way these systems usually
fail. The reasoning behind each one lives in [docs/rebuild-notes.md](docs/rebuild-notes.md).

1. **No assumed winner.** Naive trend, ridge on lagged features, a TCN, a GRU, and
   N-HiTS all race on the same split. The repo reports who actually wins, even if
   it is the boring model.
2. **Predict a distribution, not a point.** The model outputs a predictive
   distribution over future glucose. Event risk is the mass past the threshold, so
   uncertainty flows into the risk number instead of being bolted on.
3. **Time-series-aware uncertainty.** Calibration uses Adaptive Conformal Inference
   (ACI) / EnbPI, not textbook split conformal, which silently loses its coverage
   guarantee on dependent, shifting data.
4. **Honest explanations.** No pretending attention weights are reasons. Either an
   interpretable-by-design model on human-readable features, or post-hoc
   attribution with a faithfulness check.
5. **Clinical evaluation.** Clarke/Parkes error grid, event lead-time and
   sensitivity, interval calibration, false-alarm rate, and an abstention
   trade-off curve. Not just RMSE.

## what's different this time

This is a rebuild of an old project. The running log of what the first version did,
what changed, what broke along the way, and what it taught me is in
[docs/rebuild-notes.md](docs/rebuild-notes.md).

## results

First finding: on a small simglucose cohort, the simple models win. Ridge is best at
30 min (~21 mg/dL); plain **persistence** (hold the last reading) is best at 60 min
and beats ridge there. A GRU and a TCN, trained modestly, lose to both at both
horizons. That's the "simple is hard to beat on time series" result in my own
numbers, with the honest caveat that deep models are data-hungry and this cohort is
small, so it's a baseline bar, not a verdict. Full table and caveats in
[docs/eval-report.md](docs/eval-report.md); the story is in
[docs/rebuild-notes.md](docs/rebuild-notes.md).

The abstention layer earns its name. Calibrated on two patients and tested on a
held-out third, textbook conformal silently drops to 63% coverage against a 90%
promise, while Adaptive Conformal Inference recovers to 85%; under that shift the
system abstains on the calls it can't make honestly rather than guessing.

And interpretability turned out to be free: a glass-box model on 10 human-readable
features is the most accurate in the race (it beats every model at 60 min), and its
explanations are faithful by construction (0.977 on an ablation check), so each alert
says why in plain terms instead of pointing at an attention map.

Evaluated like a clinical tool, that same model puts ~97% of its predictions in the
Clarke error grid's clinically-acceptable zones and catches 78% of hypo/hyper events at
a 1% false-alarm rate.

## run it

Everything is config-driven: the knobs live in
[configs/default.yaml](configs/default.yaml), not hard-coded in scripts.

Backend (the first start simulates a small cohort and fits the model, then caches it):

```bash
pip install -e .
PYTHONPATH=src uvicorn medmaps.api.app:app --reload   # serves on :8000
```

Dashboard:

```bash
cd frontend && npm install && npm run dev             # opens on :5173
```

Reproduce the findings:

```bash
PYTHONPATH=src python scripts/race.py       # the model race
PYTHONPATH=src python scripts/abstain.py    # conformal coverage and abstention
PYTHONPATH=src python scripts/explain.py    # glass-box explanations
PYTHONPATH=src python scripts/clinical.py   # error grid and event detection
```

## roadmap

- phase 1 `done` : glucose acute-warning core, end to end (model + abstention + explanations + clinical eval + dashboard)
- phase 2 `sketching` : second vital on the same spine
- phase 3 `sketching` : medication adherence as a model feature
- phase 4 `sketching` : drift-watch lens
