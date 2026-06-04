"""Clinical evaluation, not just RMSE.

Reported metrics:
    - RMSE / MAE for context
    - Clarke and Parkes error grids: is an error clinically harmless or dangerous
    - event sensitivity and lead-time: do we catch hypos, and how early
    - interval coverage: does the 90% interval actually cover 90%
    - false-alarm rate: the real-world failure mode (alarm fatigue)
    - abstention trade-off curve: accuracy gained per unit of "I don't know"
"""
