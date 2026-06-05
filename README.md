<!-- github.com/Ananyasdrafts/medmaps -->

# MedMaps

An early-warning layer for continuous glucose monitors. It predicts a high or low
before it happens, explains the call, and would rather warn you early than miss a low.

`status: phase 1 complete`

## demo

**[Try it live](https://ananyasdrafts.github.io/medmaps/)**

![MedMaps live monitor](docs/images/demo.gif)

The dashboard plays a real CGM stream forward in time: the forecast and its
uncertainty band project ahead of "now," the alert fires *before* the event with its
reason and a phone-style notification, and a panel underneath tracks the slower "is
control slipping" picture. It is the engine's explainer view; the actual product is a
push notification on a phone.

## the sketch

People managing diabetes get a stream of glucose readings and almost no help
reading them. The dangerous moments, a low overnight, a slow loss of control over
weeks, are exactly the ones that go unnoticed until they are urgent.

MedMaps watches the stream on two timescales:

- **acute warning**: predicts an oncoming hypo (<70 mg/dL) or hyper (>180 mg/dL)
  event 30 to 60 minutes out, the window where you can still act.
- **drift watch**: a slower signal over hours and days that flags when control is
  quietly slipping, before any single reading looks alarming.

What sets it apart from the threshold alerts already on the market:

- it **explains** every alert (falling fast, insulin still active, light on carbs),
- it **cuts false alarms with context** instead of nagging (recent carbs can cover a
  coming low, recent insulin can bring down a coming high), and it flags an unreliable
  reading **out loud** ("check manually") rather than guessing or going silent,
- and it watches the **slow drift** no consumer CGM surfaces.

It is deliberately not balanced. In glucose care a missed low is far worse than a
false alarm, so the alert errs toward warning.

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

Backend:

```bash
python -m venv .venv
.venv\Scripts\activate                               # Windows (use source .venv/bin/activate elsewhere)
pip install -e .
PYTHONPATH=src python scripts/generate_cohort.py     # pre-build the demo cohort cache
PYTHONPATH=src uvicorn medmaps.api.app:app --port 8000
```

Dashboard (second terminal):

```bash
cd frontend && npm install && npm run dev            # opens on :5173
```

Reproduce the findings:

```bash
PYTHONPATH=src python scripts/race.py       # the model race
PYTHONPATH=src python scripts/abstain.py    # conformal coverage and abstention
PYTHONPATH=src python scripts/explain.py    # glass-box explanations
PYTHONPATH=src python scripts/clinical.py   # error grid and event detection
```

## roadmap

- phase 1 `done` : glucose early-warning, end to end — model race, conformal abstention, glass-box explanations, clinical eval, safety-asymmetric alerts, drift watch, light personalization, and the live-monitor dashboard
- next `sketching` : a second vital on the same spine, deeper personalization, a hosted demo
