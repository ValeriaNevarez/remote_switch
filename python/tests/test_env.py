"""Unit tests for environment-variable helpers in ``env.py``."""

from __future__ import annotations

import base64
import json
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from env import load_json_from_base64_env, load_string_from_env


class TestLoadStringFromEnv(unittest.TestCase):
    def test_returns_trimmed_value(self) -> None:
        with patch.dict(os.environ, {"DEMO_VAR": "  hello  "}, clear=False):
            self.assertEqual(load_string_from_env("DEMO_VAR"), "hello")

    def test_raises_for_missing_or_empty_var(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(RuntimeError):
                load_string_from_env("MISSING")


class TestLoadJsonFromBase64Env(unittest.TestCase):
    def test_decodes_and_parses_json(self) -> None:
        payload = {"name": "switch", "enabled": True}
        encoded = base64.b64encode(json.dumps(payload).encode("utf-8")).decode("utf-8")
        with patch.dict(os.environ, {"JSON_B64": encoded}, clear=False):
            self.assertEqual(load_json_from_base64_env("JSON_B64"), payload)

    def test_raises_for_invalid_base64(self) -> None:
        with patch.dict(os.environ, {"JSON_B64": "not-base64"}, clear=False):
            with self.assertRaises(RuntimeError):
                load_json_from_base64_env("JSON_B64")


if __name__ == "__main__":
    unittest.main()
