# Rebuild notes

A running, honest log of rebuilding MedMaps with what I know now. This doubles as
the source for the LinkedIn write-up, so it stays narrative, not bullet soup.

## the original

The first MedMaps was a hackathon project: an LSTM (later with an attention layer)
that predicted health risk from time-series vitals. It worked in the sense that it
produced numbers. Looking back, it had the three flaws almost every student health
model has:

1. it reported a confident prediction no matter how little it actually knew,
2. it was evaluated on RMSE, which says nothing about whether an error is
   clinically dangerous, and
3. the "interpretability" was an attention heatmap, which I now know is not a
   faithful explanation.

## what I'm doing differently, and why

### 1. it can say "I don't know"
The single biggest change. The old model never abstained. The new one wraps its
forecast in a calibrated interval and refuses to fire when the signal is thin or
out of distribution. This is the same lesson my drowsiness detector taught me the
hard way: a system that fails silently is worse than one that admits uncertainty.

### 2. no assumed winner
Old me reached straight for the fanciest model. New me runs a race, naive trend,
ridge on lags, TCN, GRU, N-HiTS, on the same split and reports who wins. There is
real evidence that simple models beat Transformers on time series (DLinear, AAAI
2023), so the result is not a foregone conclusion. If the boring model wins, that
goes in the report.

### 3. the uncertainty is the right kind
My first instinct was textbook conformal prediction. It assumes exchangeability,
which glucose data violates, so the coverage guarantee quietly disappears. The
rebuild uses Adaptive Conformal Inference / EnbPI instead. I plan to show the
broken version next to the correct one, because the failure is the lesson.

### 4. honest explanations
Dropping attention-as-explanation. Either a glass-box model on human-readable
features (trend, variability, time since last insulin), or a real attribution
method with a faithfulness check. An explanation I can't trust is worse than none.

### 5. evaluation a clinician would recognize
Error-grid analysis, event lead-time and sensitivity, interval calibration, and
false-alarm rate, instead of a lonely RMSE number.

## what broke

**simglucose vs Python 3.13.** First wall of the rebuild. simglucose depends on the
old `gym`, which imports `distutils`, removed from the standard library in Python
3.12. A fresh venv doesn't seed `setuptools` anymore, so there was nothing to
provide the `distutils` shim and the import died immediately. Fix: pin
`setuptools<81`, whose precedence hook restores `distutils` at interpreter startup.
That kept the whole project on 3.13 instead of forcing a separate 3.11 environment.
Worth remembering that "just pip install it" hides a surprising amount of
dependency archaeology, and that the newest Python is not always the friendliest.

## findings

(notable results land here and get surfaced in the README)
