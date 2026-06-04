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

Findings and the full evaluation go in [docs/eval-report.md](docs/eval-report.md)
as they land. Headline observations will be surfaced here.

## run it

Coming together during phase 1. The pipeline is config-driven: everything in
[configs/default.yaml](configs/default.yaml), nothing hard-coded in scripts.

## roadmap

- phase 1 `building` : glucose acute-warning core, end to end
- phase 2 `sketching` : second vital on the same spine
- phase 3 `sketching` : medication adherence as a model feature
- phase 4 `sketching` : drift-watch lens
