"""Load the repository-wide JSON config (shared with the JavaScript app)."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import TypedDict, cast

_REPO_ROOT = Path(__file__).resolve().parent.parent
_CONFIG_PATH = _REPO_ROOT / "config.json"


class Config(TypedDict):
    twilio_master_phone_number: str
    from_email: str
    to_email: str
    cc_emails: str


_REQUIRED_KEYS: tuple[str, ...] = tuple(Config.__annotations__)


@lru_cache(maxsize=1)
def load_config() -> Config:
    if not _CONFIG_PATH.is_file():
        raise RuntimeError(f"Missing config file: {_CONFIG_PATH}")
    with _CONFIG_PATH.open(encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise RuntimeError(f"Config must be a JSON object: {_CONFIG_PATH}")
    missing = [key for key in _REQUIRED_KEYS if key not in data]
    if missing:
        raise RuntimeError(f"Config {_CONFIG_PATH} is missing required keys: {missing}")
    return cast(Config, data)
