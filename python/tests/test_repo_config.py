"""Unit tests for ``repo_config.load_config`` validation behavior."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import repo_config


def _valid_config() -> dict[str, str | int]:
    return {
        "twilio_master_phone_number": "+5215555555555",
        "from_email": "from@example.com",
        "weekly_report_to_email": "weekly@example.com",
        "weekly_report_cc_emails": "weekly-cc@example.com",
        "toku_sync_to_email": "toku@example.com",
        "toku_sync_cc_emails": "toku-cc@example.com",
        "toku_sync_grace_period_days": 10,
        "toku_sync_max_call_retries": 2,
    }


class TestLoadConfig(unittest.TestCase):
    def tearDown(self) -> None:
        repo_config.load_config.cache_clear()

    def test_loads_valid_json_object(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            config_path = Path(tmp) / "config.json"
            config_path.write_text(json.dumps(_valid_config()), encoding="utf-8")
            with patch.object(repo_config, "_CONFIG_PATH", config_path):
                config = repo_config.load_config()
                self.assertEqual(config["weekly_report_to_email"], "weekly@example.com")
                self.assertEqual(config["toku_sync_to_email"], "toku@example.com")
                self.assertEqual(config["toku_sync_grace_period_days"], 10)

    def test_raises_when_required_keys_are_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            config_path = Path(tmp) / "config.json"
            config_path.write_text(
                json.dumps({"from_email": "from@example.com"}),
                encoding="utf-8",
            )
            with patch.object(repo_config, "_CONFIG_PATH", config_path):
                with self.assertRaises(RuntimeError):
                    repo_config.load_config()


if __name__ == "__main__":
    unittest.main()
