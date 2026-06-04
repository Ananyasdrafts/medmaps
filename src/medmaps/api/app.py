"""FastAPI app. One predict endpoint that returns the forecast, the calibrated
interval, the plain-language drivers, and the honest abstain flag, plus a sample
endpoint so the dashboard has real windows to show.
"""

from __future__ import annotations

from functools import lru_cache

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from medmaps.api.service import MedMapsService

app = FastAPI(title="MedMaps", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@lru_cache(maxsize=1)
def get_service() -> MedMapsService:
    return MedMapsService()


class WindowRequest(BaseModel):
    window: list[list[float]]


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/sample")
def sample(event: bool = False, service: MedMapsService = Depends(get_service)) -> dict:
    return service.sample_window(event=event)


@app.post("/predict")
def predict(req: WindowRequest, service: MedMapsService = Depends(get_service)) -> dict:
    return service.predict_window(req.window)
