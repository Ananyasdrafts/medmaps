"""Alert-policy tests. Pure numpy, runs in CI."""

from medmaps.alerts import decide_alert


def _flat(v, n=12):
    return [v] * n


def test_unreliable_reading_fails_loud_not_silent():
    a = decide_alert(_flat(100), _flat(90), _flat(110), reliable=False)
    assert a["level"] == "verify"  # never "ok" or silence


def test_likely_low_alerts():
    # midpoint dips below hypo
    a = decide_alert(_flat(62), _flat(45), _flat(80))
    assert a["level"] == "alert" and a["kind"] == "hypo"
    assert a["lead_min"] == 5


def test_plausible_low_alerts_when_no_carbs():
    # midpoint fine, but lower edge crosses hypo -> sensitivity-biased alert
    a = decide_alert(_flat(95), _flat(65), _flat(125), carbs_recent=0)
    assert a["level"] == "alert" and a["kind"] == "hypo"


def test_plausible_low_downgrades_to_watch_with_carbs():
    a = decide_alert(_flat(95), _flat(65), _flat(125), carbs_recent=45)
    assert a["level"] == "watch" and a["kind"] == "hypo"


def test_plausible_high_downgrades_to_watch_with_insulin():
    a = decide_alert(_flat(160), _flat(140), _flat(195), recent_insulin=True)
    assert a["level"] == "watch" and a["kind"] == "hyper"


def test_in_range_is_ok():
    a = decide_alert(_flat(110), _flat(95), _flat(130))
    assert a["level"] == "ok" and a["kind"] is None
