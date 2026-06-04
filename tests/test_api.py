"""API tests. Skipped where fastapi/sklearn/httpx aren't installed (e.g. CI).
Uses a synthetic cohort so no simglucose is needed."""

import numpy as np
import pandas as pd
import pytest

pytest.importorskip("sklearn")
pytest.importorskip("fastapi")
pytest.importorskip("httpx")

from fastapi.testclient import TestClient  # noqa: E402

from medmaps.api.app import app, get_service  # noqa: E402
from medmaps.api.service import MedMapsService  # noqa: E402


def _cohort(n=400):
    rng = np.random.default_rng(0)
    frames = []
    for name in ["p1", "p2"]:
        t = pd.date_range("2024-01-01", periods=n, freq="5min")
        cgm = 120 + 40 * np.sin(np.linspace(0, 12, n)) + rng.normal(0, 3, n)
        frames.append(
            pd.DataFrame(
                {"time": t, "cgm": cgm, "cho": 0.0, "bolus": 0.0, "basal": 0.01, "patient": name}
            )
        )
    return pd.concat(frames, ignore_index=True)


@pytest.fixture
def client():
    service = MedMapsService(cohort=_cohort())
    app.dependency_overrides[get_service] = lambda: service
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}


def test_sample_then_predict_round_trip(client):
    s = client.get("/sample").json()
    assert len(s["window"]) > 0
    assert len(s["history_cgm"]) == len(s["window"])

    r = client.post("/predict", json={"window": s["window"]}).json()
    assert len(r["forecast"]) == len(r["horizon_minutes"]) == len(r["lower"]) == len(r["upper"])
    assert len(r["drivers"]) == 3
    assert all("feature" in d and "contribution" in d for d in r["drivers"])
    assert isinstance(r["abstain"], bool)
    assert len(r["risk"]) >= 1
    assert r["thresholds"] == {"hypo": 70, "hyper": 180}
