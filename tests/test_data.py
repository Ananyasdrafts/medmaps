"""Data-generation tests. Skipped where simglucose isn't installed (e.g. CI)."""

import pytest

pytest.importorskip("simglucose")

from medmaps.data.simulate import simulate_cohort, simulate_patient  # noqa: E402


def test_simulate_patient_is_well_formed():
    df = simulate_patient("adolescent#001", days=1, sample_minutes=5, missed_bolus_prob=0.2, seed=1)
    assert list(df.columns) == ["time", "cgm", "cho", "bolus", "basal", "bolus_skipped", "patient"]
    assert len(df) == int(24 * 60 / 5)  # one day on a 5-minute grid
    assert df["cgm"].notna().all()
    assert df["cgm"].between(10, 600).all()  # physiologically plausible CGM range
    assert df["bolus_skipped"].dtype == bool


def test_simulate_cohort_stacks_patients():
    df = simulate_cohort(
        ["adolescent#001", "adult#001"], days=1, sample_minutes=5, missed_bolus_prob=0.1, seed=1
    )
    assert df["patient"].nunique() == 2
