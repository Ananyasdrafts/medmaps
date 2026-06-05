"""Scenario-builder tests. Skipped without sklearn (glass-box). Synthetic cohort."""

import numpy as np
import pandas as pd
import pytest

pytest.importorskip("sklearn")

from medmaps.api.service import MedMapsService  # noqa: E402


def _cohort_with_event(n=320):
    # smooth sinusoid whose troughs dip below the hypo threshold; the descent is
    # gradual and therefore forecastable, so the model can warn ahead of it.
    frames = []
    for name in ["p1", "p2"]:
        t = pd.date_range("2024-01-01", periods=n, freq="5min")
        cgm = 115 + 55 * np.sin(np.linspace(0, 14, n))
        frames.append(
            pd.DataFrame(
                {"time": t, "cgm": cgm, "cho": 0.0, "bolus": 0.0, "basal": 0.01, "patient": name}
            )
        )
    return pd.concat(frames, ignore_index=True)


@pytest.fixture(scope="module")
def service():
    return MedMapsService(cohort=_cohort_with_event())


def test_scenario_has_playable_frames(service):
    sc = service.build_scenario(kind="event")
    assert sc["frames"] and sc["actual"]
    frame = sc["frames"][0]
    assert {"now_min", "forecast", "lower", "upper", "alert", "drivers", "drift"} <= set(frame)
    assert len(frame["forecast"]) == len(sc["horizon_minutes"])
    assert frame["alert"]["level"] in {"ok", "watch", "alert", "verify"}


def test_scenario_raises_an_alert_before_the_low(service):
    sc = service.build_scenario(kind="event")
    assert any(f["alert"]["level"] in ("alert", "watch") for f in sc["frames"])
