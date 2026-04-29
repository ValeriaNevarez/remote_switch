"""Unit tests for ``twilio_api.TwilioClient`` logic."""

from __future__ import annotations

import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from twilio_api import TwilioClient


def _record(*, status: str, duration: str | None, created: datetime) -> SimpleNamespace:
    return SimpleNamespace(status=status, duration=duration, date_created=created)


class _CallsApi:
    def __init__(self, records: list[SimpleNamespace]):
        self._records = records

    def list(self, **kwargs):
        if kwargs.get("status") == "completed":
            return [r for r in self._records if r.status == "completed"]
        limit = kwargs.get("limit")
        if limit is not None:
            return self._records[:limit]
        return self._records


class _FakeTwilioRestClient:
    def __init__(self, records: list[SimpleNamespace]):
        self.calls = _CallsApi(records)
        self.messages = SimpleNamespace(create=lambda **kwargs: SimpleNamespace(sid="msg-1"))


class TestTwilioClient(unittest.TestCase):
    def test_last_call_completed_but_short_is_reported_incompleted(self) -> None:
        records = [
            _record(
                status="completed",
                duration="59",
                created=datetime(2026, 4, 1, tzinfo=timezone.utc),
            )
        ]
        with patch("twilio_api.Client", return_value=_FakeTwilioRestClient(records)):
            client = TwilioClient("sid", "token", "+1")
            status = client.get_last_call_status("+2")
            self.assertIsNotNone(status)
            self.assertEqual(status.status, "incompleted")

    def test_last_completed_call_date_accepts_threshold_duration(self) -> None:
        created = datetime(2026, 4, 1, tzinfo=timezone.utc)
        records = [_record(status="completed", duration="60", created=created)]
        with patch("twilio_api.Client", return_value=_FakeTwilioRestClient(records)):
            client = TwilioClient("sid", "token", "+1")
            last_date = client.get_last_completed_call_date("+2")
            self.assertEqual(last_date, created)


if __name__ == "__main__":
    unittest.main()
