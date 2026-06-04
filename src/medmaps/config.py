"""Config loading. Everything experiment-facing lives in YAML, not in code."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

_DEFAULT = Path(__file__).resolve().parents[2] / "configs" / "default.yaml"


def load_config(path: str | Path | None = None) -> dict[str, Any]:
    """Load a MedMaps config. Falls back to configs/default.yaml."""
    path = Path(path) if path is not None else _DEFAULT
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)
