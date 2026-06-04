"""The alerting policy.

In glucose care a missed low is far worse than a false alarm, so this is
deliberately not balanced. It is sensitivity-biased (it warns on a *plausible* low,
judged by the lower edge of the forecast interval, not just the midpoint), it never
goes silent on an unreliable reading (it says "check manually" out loud), and it uses
context to downgrade nuisance alarms to a quieter "watch" rather than suppressing
them: recent carbs can cover a coming low, recent insulin can bring down a coming
high. Downgrades never reach silence.

Levels: alert (act now), watch (keep an eye on it), verify (reading untrustworthy,
check manually), ok.
"""

from __future__ import annotations

import numpy as np

HYPO = 70.0
HYPER = 180.0
CARB_COVER = 30.0  # grams of recent carbs assumed able to cover a mild coming low
POINT_MARGIN = 5.0  # mg/dL; how close the midpoint must be to call a risk "likely"


def decide_alert(
    forecast,
    lower,
    upper,
    *,
    hypo: float = HYPO,
    hyper: float = HYPER,
    carbs_recent: float = 0.0,
    recent_insulin: bool = False,
    reliable: bool = True,
    sample_minutes: int = 5,
) -> dict:
    """Turn a forecast (and its interval and context) into a safety-biased alert."""
    if not reliable:
        return {
            "level": "verify",
            "kind": None,
            "lead_min": None,
            "reason": "this reading looks unreliable, check your glucose manually",
        }

    forecast = np.asarray(forecast, dtype=float)
    lower = np.asarray(lower, dtype=float)
    upper = np.asarray(upper, dtype=float)
    n = len(forecast)

    hypo_idx = next((h for h in range(n) if lower[h] < hypo), None)
    hyper_idx = next((h for h in range(n) if upper[h] > hyper), None)

    # a coming low takes priority: it is the acute danger
    if hypo_idx is not None:
        lead = (hypo_idx + 1) * sample_minutes
        if forecast[hypo_idx] < hypo + POINT_MARGIN:
            return {"level": "alert", "kind": "hypo", "lead_min": lead,
                    "reason": f"likely low within {lead} min"}
        if carbs_recent >= CARB_COVER:
            return {"level": "watch", "kind": "hypo", "lead_min": lead,
                    "reason": "possible low, but recent carbs may cover it"}
        return {"level": "alert", "kind": "hypo", "lead_min": lead,
                "reason": f"possible low within {lead} min"}

    if hyper_idx is not None:
        lead = (hyper_idx + 1) * sample_minutes
        if forecast[hyper_idx] > hyper - POINT_MARGIN:
            return {"level": "alert", "kind": "hyper", "lead_min": lead,
                    "reason": f"likely high within {lead} min"}
        if recent_insulin:
            return {"level": "watch", "kind": "hyper", "lead_min": lead,
                    "reason": "possible high, but recent insulin should bring it down"}
        return {"level": "alert", "kind": "hyper", "lead_min": lead,
                "reason": f"possible high within {lead} min"}

    return {"level": "ok", "kind": None, "lead_min": None,
            "reason": "in range, no concern in the next hour"}
