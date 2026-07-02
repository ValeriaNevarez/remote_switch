"""Unit tests for ``switch_caller.SwitchCaller``."""

from __future__ import annotations

import sys
import unittest
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from switch_caller import SwitchCaller
from twilio_api import LastCallStatus

from tests.fakes import RecordingSleep


class FakeTwilioClient:
    """Minimal Twilio stub for :class:`SwitchCaller` tests."""

    def __init__(self) -> None:
        self.created_calls: list[dict[str, object]] = []
        self._status_queues: dict[str, list[str | None]] = defaultdict(list)

    def create_call(
        self,
        *,
        to: str,
        twiml: str,
        time_limit_seconds: int = 70,
        status_callback_url: str | None = None,
    ) -> str:
        self.created_calls.append(
            {
                "to": to,
                "twiml": twiml,
                "time_limit_seconds": time_limit_seconds,
                "status_callback_url": status_callback_url,
            }
        )
        return f"SID-{len(self.created_calls)}"

    def send_message(self, *, to: str, text: str) -> str:
        return "MSG-1"

    def set_status_sequence(
        self, phone_number: str, statuses: list[str | None]
    ) -> None:
        self._status_queues[phone_number] = list(statuses)

    def get_last_call_status(
        self,
        phone_number: str,
        min_completed_duration_seconds: int = 60,
    ) -> LastCallStatus | None:
        queue = self._status_queues.get(phone_number, [])
        if not queue:
            return None
        status = queue.pop(0)
        if status is None:
            return None
        return LastCallStatus(status=status, date=datetime.now(timezone.utc))


class TestCallSwitchWithRetries(unittest.TestCase):
    def setUp(self) -> None:
        self.twilio = FakeTwilioClient()
        self.sleep = RecordingSleep()
        self.caller = SwitchCaller(
            twilio=self.twilio,
            master_phone_number="+19999999999",
            sleep=self.sleep,
        )

    def test_stops_after_first_completed_call(self) -> None:
        self.twilio.set_status_sequence("+1", ["completed"])

        sid, succeeded = self.caller.call_switch_with_retries(
            "+1", True, max_retries=3
        )

        self.assertTrue(succeeded)
        self.assertEqual(sid, "SID-1")
        self.assertEqual(len(self.twilio.created_calls), 1)
        self.assertEqual(self.sleep.durations, [85])

    def test_retries_until_completed(self) -> None:
        self.twilio.set_status_sequence("+1", ["busy", "failed", "completed"])

        sid, succeeded = self.caller.call_switch_with_retries(
            "+1", False, max_retries=3
        )

        self.assertTrue(succeeded)
        self.assertEqual(sid, "SID-3")
        self.assertEqual(len(self.twilio.created_calls), 3)
        self.assertEqual(self.sleep.durations, [85, 10, 85, 10, 85])

    def test_exhausts_retries_when_never_completed(self) -> None:
        self.twilio.set_status_sequence("+1", ["busy", "busy", "busy"])

        sid, succeeded = self.caller.call_switch_with_retries(
            "+1", True, max_retries=2
        )

        self.assertFalse(succeeded)
        self.assertEqual(sid, "SID-3")
        self.assertEqual(len(self.twilio.created_calls), 3)
        self.assertEqual(self.sleep.durations, [85, 10, 85, 10, 85])

    def test_retries_when_no_call_record_yet(self) -> None:
        self.twilio.set_status_sequence("+1", [None, None, "completed"])

        sid, succeeded = self.caller.call_switch_with_retries(
            "+1", True, max_retries=2
        )

        self.assertTrue(succeeded)
        self.assertEqual(sid, "SID-3")
        self.assertEqual(len(self.twilio.created_calls), 3)
        self.assertEqual(self.sleep.durations, [85, 10, 85, 10, 85])


if __name__ == "__main__":
    unittest.main()
