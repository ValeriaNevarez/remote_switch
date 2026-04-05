"""Load values from environment variables (plain strings or base64-encoded JSON)."""

from __future__ import annotations

import base64
import json
import os
from typing import Any


def _require_nonempty_str(var_name: str, expectation: str) -> str:
    value = os.environ.get(var_name, "").strip()
    if not value:
        raise RuntimeError(
            f"Environment variable {var_name!r} is not set or is empty ({expectation})."
        )
    return value


def load_string_from_env(var_name: str) -> str:
    """
    Return the trimmed value of ``var_name``.

    Raises:
        RuntimeError: If the variable is missing or empty after stripping.
    """
    return _require_nonempty_str(var_name, "expected a non-empty string")


def load_json_from_base64_env(var_name: str) -> Any:
    """
    Read ``var_name`` from the environment, base64-decode it, and parse as UTF-8 JSON.

    Raises:
        RuntimeError: If the variable is missing, empty, not valid base64, or not valid JSON.
    """
    b64 = _require_nonempty_str(var_name, "expected base64-encoded UTF-8 JSON")
    try:
        raw = base64.b64decode(b64)
        return json.loads(raw.decode("utf-8"))
    except Exception as e:
        raise RuntimeError(
            f"Environment variable {var_name!r} must be valid base64 of UTF-8 JSON: {e}"
        ) from e
