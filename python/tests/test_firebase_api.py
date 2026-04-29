"""Unit tests for parsing behavior in ``firebase_api``."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from firebase_api import FirebaseClient


class TestParseDevice(unittest.TestCase):
    def test_raises_with_key_context_when_required_field_missing(self) -> None:
        incomplete = {
            "serial_number": "1",
            "phone_number": "+1",
            "enabled": True,
            "is_active": True,
            "client_name": "Acme",
            # missing client_number
            "is_manual_override": False,
            "is_payment_current": True,
        }
        with self.assertRaises(RuntimeError) as err:
            FirebaseClient._parse_device(incomplete, key="abc123")
        message = str(err.exception)
        self.assertIn("/devices/abc123", message)
        self.assertIn("client_number", message)


class TestPayloadNormalization(unittest.TestCase):
    def test_payload_to_keyed_items_from_dict_preserves_keys(self) -> None:
        payload = {
            "95": {"serial_number": "67"},
            "64": {"serial_number": "42"},
        }
        keyed = FirebaseClient._payload_to_keyed_items(payload)
        self.assertEqual({key for key, _ in keyed}, {"95", "64"})

    def test_payload_to_keyed_items_from_list_uses_indices(self) -> None:
        payload = [
            None,
            {"serial_number": "1"},
            "bad",
            {"serial_number": "2"},
        ]
        keyed = FirebaseClient._payload_to_keyed_items(payload)
        self.assertEqual(keyed, [("1", {"serial_number": "1"}), ("3", {"serial_number": "2"})])


if __name__ == "__main__":
    unittest.main()
