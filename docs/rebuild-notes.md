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

**The abstention layer, doing its job.** This is the part I most wanted to get right,
and the demo did exactly what I hoped and feared. Calibrated on two patients, textbook
split conformal covers only 63% of a held-out third while still promising 90%. The
exchangeability assumption breaks the instant the test patient differs, and the
guarantee evaporates silently, which is the whole danger. Adaptive Conformal Inference,
nudging its level as it sees misses, climbs back to 85%. Under that shift the honest
intervals widen to about 89 mg/dL, so with an actionability threshold the system
abstains on most predictions for that patient. That is not a bug, it is the system
refusing to pretend it understands someone it never saw. The lesson I did not expect to
write down: abstaining on interval width handles variance, not bias. A model that is
systematically wrong for a new population needs more representative data, not just
wider error bars. Saying that plainly is the difference between a system that knows its
limits and one that hides them.

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

**The baseline bites back (first race).** Before any deep model, I raced two naive
baselines and a ridge regression. The result is a good lesson in not trusting your
own framing. I'd assumed a naive baseline would be hard to beat at 30 minutes, and
it is, but only once you pick the *right* naive. My first one extrapolated the
recent slope, which overshoots and lands worst of the three (RMSE 61 at 60 min). The
honest baseline is persistence, just holding the last reading: it scores 23.7 at 30
min, within 2.5 mg/dL of ridge, and actually beats ridge at 60 min (36.1 vs 39.0).

So the ranking flips with horizon, and the trivial model wins at the longer one.
That sets a clean, slightly humbling bar for everything that follows: a TCN, a GRU,
or N-HiTS now has to beat *persistence* at both horizons, especially 60 minutes, or
it has not earned its parameters. This is exactly the "simple is hard to beat on
time series" story (DLinear) showing up in my own numbers, on the first try.

**The deep models lost.** I added a GRU and a TCN expecting at least the GRU to pull
ahead. It didn't. Both land behind ridge and persistence at both horizons (GRU 30.1
/ 44.3, TCN 28.7 / 47.8). The old me would have been tempted to quietly tune until
the deep model "won," call it a success, and move on. The honest read is that on a
small cohort with modest training, the extra capacity is a liability, not an asset,
and writing that down is the point. It is not a claim that deep models are useless
for glucose; they are data-hungry and I have barely fed them. The fair rematch is a
much larger cohort with tuned models. But today, the boring model wins, and the repo
says so out loud. That honesty is worth more than a cherry-picked deep-learning win.
