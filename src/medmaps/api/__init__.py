"""FastAPI serving layer.

One endpoint takes a recent window of readings and returns: the distributional
forecast, the event risk per horizon, the calibrated interval, a short explanation,
and an explicit abstain flag when the model should stay quiet. The React dashboard
renders exactly this, including the honest "not enough signal" state.
"""
