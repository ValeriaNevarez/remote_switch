"""Load repository-wide JSON config (shared with the JavaScript app)."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
_CONFIG_PATH = _REPO_ROOT / "config.json"


@lru_cache(maxsize=1)
def load_config() -> dict:
    if not _CONFIG_PATH.is_file():
        raise RuntimeError(f"Missing config file: {_CONFIG_PATH}")
    with _CONFIG_PATH.open(encoding="utf-8") as f:
        return json.load(f)
