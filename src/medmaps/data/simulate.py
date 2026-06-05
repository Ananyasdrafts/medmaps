"""Generate CGM cohorts with simglucose and inject medication-adherence scenarios.

simglucose wraps an FDA-accepted T1D simulator. Each virtual patient is driven by a
basal-bolus controller while RandomScenario produces realistic meals. Non-adherence
is injected by skipping meal boluses with a configurable probability, which is the
medication-adherence signal the risk model later learns from. Output is one tidy,
uniformly resampled DataFrame per patient.
"""

from __future__ import annotations

from datetime import datetime, timedelta

import numpy as np
import pandas as pd

_START = datetime(2024, 1, 1, 0, 0, 0)


def simulate_patient(
    name: str,
    days: int,
    sample_minutes: int,
    missed_bolus_prob: float = 0.0,
    seed: int = 0,
) -> pd.DataFrame:
    """Simulate one patient and return a uniform-cadence frame.

    Columns: time, cgm, cho (carbs g), bolus (U), basal (U/min), bolus_skipped, patient.
    """
    # imported lazily so the rest of the package (and CI) does not require simglucose
    from simglucose.actuator.pump import InsulinPump
    from simglucose.controller.base import Action
    from simglucose.controller.basal_bolus_ctrller import BBController
    from simglucose.patient.t1dpatient import T1DPatient
    from simglucose.sensor.cgm import CGMSensor
    from simglucose.simulation.env import T1DSimEnv
    from simglucose.simulation.scenario_gen import RandomScenario

    rng = np.random.default_rng(seed)
    patient = T1DPatient.withName(name)
    sensor = CGMSensor.withName("Dexcom", seed=seed)
    pump = InsulinPump.withName("Insulet")
    scenario = RandomScenario(start_time=_START, seed=seed)
    env = T1DSimEnv(patient, sensor, pump, scenario)
    ctrl = BBController()

    step_min = int(sensor.sample_time)
    n_steps = int(days * 24 * 60 / step_min)

    obs, reward, done, info = env.reset()
    t = _START
    rows = []
    for _ in range(n_steps):
        action = ctrl.policy(obs, reward, done, **info)
        meal = float(info.get("meal", 0.0) or 0.0)
        skipped = False
        # a meal bolus that the patient does not take: the adherence signal
        if meal > 0 and action.bolus > 0 and rng.random() < missed_bolus_prob:
            action = Action(basal=action.basal, bolus=0.0)
            skipped = True
        rows.append(
            {
                "time": t,
                "cgm": float(obs.CGM),
                "cho": meal,
                "bolus": float(action.bolus),
                "basal": float(action.basal),
                "bolus_skipped": skipped,
            }
        )
        obs, reward, done, info = env.step(action)
        t += timedelta(minutes=step_min)

    raw = pd.DataFrame(rows).set_index("time")
    rule = f"{sample_minutes}min"
    out = pd.DataFrame(
        {
            "cgm": raw["cgm"].resample(rule).mean().interpolate(),
            "cho": raw["cho"].resample(rule).sum(),
            "bolus": raw["bolus"].resample(rule).sum(),
            "basal": raw["basal"].resample(rule).mean(),
            "bolus_skipped": raw["bolus_skipped"].resample(rule).max().fillna(False).astype(bool),
        }
    )
    out["patient"] = name
    return out.reset_index()


def simulate_cohort(
    names: list[str],
    days: int,
    sample_minutes: int,
    missed_bolus_prob: float = 0.0,
    seed: int = 0,
) -> pd.DataFrame:
    """Simulate several patients (a distinct seed each) and stack them."""
    frames = [
        simulate_patient(name, days, sample_minutes, missed_bolus_prob, seed + i)
        for i, name in enumerate(names)
    ]
    return pd.concat(frames, ignore_index=True)
