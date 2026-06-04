"""Clinical-metric tests. Pure numpy, runs in CI."""

import numpy as np

from medmaps.eval.clinical import (
    clarke_zones,
    event_detection,
    lead_times,
    zone_percentages,
)


def test_clarke_zones_known_points():
    # exact match -> A; opposite extreme -> E; high but within 20% -> A; modest miss -> B
    z = clarke_zones([100, 50, 300, 100], [100, 200, 305, 130])
    assert z.tolist() == ["A", "E", "A", "B"]


def test_zone_percentages_sum_to_100():
    z = clarke_zones([100, 100, 100, 100], [100, 100, 130, 130])
    pct = zone_percentages(z)
    assert abs(sum(pct.values()) - 100.0) < 1e-6
    assert pct["A"] == 50.0 and pct["B"] == 50.0


def test_event_detection_counts():
    true_traj = np.array([[100, 100, 60, 100], [120, 120, 120, 120], [120, 120, 120, 120]])
    pred_traj = np.array([[100, 100, 65, 100], [120, 120, 120, 120], [120, 60, 120, 120]])
    ev = event_detection(true_traj, pred_traj)
    assert ev["sensitivity"] == 1.0      # the real hypo was caught
    assert ev["false_alarm_rate"] == 0.5  # one false alarm out of two non-events
    assert ev["tp"] == 1 and ev["fp"] == 1


def test_lead_time_is_minutes_to_first_crossing():
    true_traj = np.array([[100, 100, 60, 100]])
    pred_traj = np.array([[100, 100, 65, 100]])
    lt = lead_times(true_traj, pred_traj, sample_minutes=5)
    assert lt.tolist() == [15.0]  # first crossing at index 2 -> (2+1)*5
