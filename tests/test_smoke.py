"""Smoke tests: the package imports and the config is well-formed.
Real model/eval tests arrive with the code they cover."""

import medmaps
from medmaps.config import load_config


def test_package_imports():
    assert medmaps.__version__


def test_default_config_is_sane():
    cfg = load_config()
    # the design decisions that must not silently drift
    assert cfg["task"]["horizons_minutes"] == [30, 60]
    assert cfg["uncertainty"]["method"] in {"aci", "enbpi"}
    assert cfg["abstention"]["ood_detection"] is True
    assert "error_grid" in cfg["eval"]["metrics"]
    assert cfg["drift_watch"]["changepoint"] is True
