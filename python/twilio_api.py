"""Thin wrapper around the Twilio REST client used by the remote-switch tools."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from functools import lru_cache

from twilio.rest import Client

from env import load_string_from_env
from repo_config import load_config

DEFAULT_OUTBOUND_TIME_LIMIT_SECONDS = 70
COMPLETED_CALL_MIN_DURATION_SECONDS = 60


@dataclass(frozen=True)
class LastCallStatus:
    """Most recent call to a phone number, normalized for our reporting needs."""

    status: str
    date: datetime | None


@dataclass(frozen=True)
class TwilioCallRecord:
    """Small subset of a Twilio Call record needed by local diagnostics."""

    sid: str
    status: str
    date: datetime | None
    duration_seconds: int | None
    to: str
    from_: str


class TwilioClient:
    def __init__(self, account_sid: str, auth_token: str, from_number: str):
        self._client = Client(account_sid, auth_token)
        self.from_number = from_number

    @staticmethod
    def _parse_duration_seconds(duration: str | None) -> int | None:
        if duration is None:
            return None
        try:
            return int(duration)
        except (TypeError, ValueError):
            return None

    def send_message(self, *, to: str, text: str) -> str:
        message = self._client.messages.create(
            from_=self.from_number,
            body=text,
            to=to,
        )
        return str(message.sid)

    def create_call(
        self,
        *,
        to: str,
        twiml: str,
        time_limit_seconds: int = DEFAULT_OUTBOUND_TIME_LIMIT_SECONDS,
    ) -> str:
        call = self._client.calls.create(
            from_=self.from_number,
            to=to,
            twiml=twiml,
            time_limit=time_limit_seconds,
        )
        return str(call.sid)

    def get_last_call_status(
        self,
        phone_number: str,
        min_completed_duration_seconds: int = COMPLETED_CALL_MIN_DURATION_SECONDS,
    ) -> LastCallStatus | None:
        """
        Return the most recent call to ``phone_number``, or None if there are no
        recorded calls. A call recorded by Twilio as "completed" but shorter than
        ``min_completed_duration_seconds`` is reported as "incompleted".
        """
        records = self._client.calls.list(limit=1, to=phone_number)
        if not records:
            return None

        record = records[0]
        status = str(record.status)
        duration = self._parse_duration_seconds(record.duration)
        if (
            status == "completed"
            and duration is not None
            and duration < min_completed_duration_seconds
        ):
            status = "incompleted"
        return LastCallStatus(status=status, date=record.date_created)

    def get_last_completed_call_date(
        self,
        phone_number: str,
        min_duration_seconds: int = COMPLETED_CALL_MIN_DURATION_SECONDS,
    ) -> datetime | None:
        """Return the timestamp of the most recent "real" completed call, if any."""
        records = self._client.calls.list(to=phone_number, status="completed")
        for record in records:
            duration = self._parse_duration_seconds(record.duration)
            if duration is not None and duration >= min_duration_seconds:
                return record.date_created
        return None

    def get_last_call_record(self, phone_number: str) -> TwilioCallRecord | None:
        """Return the most recent raw call record summary for ``phone_number``."""
        records = self._client.calls.list(limit=1, to=phone_number)
        if not records:
            return None

        record = records[0]
        return TwilioCallRecord(
            sid=str(record.sid),
            status=str(record.status),
            date=record.date_created,
            duration_seconds=self._parse_duration_seconds(record.duration),
            to=str(record.to),
            from_=str(getattr(record, "from_", getattr(record, "_from", ""))),
        )

    def get_call_events(self, call_sid: str, *, limit: int = 20) -> list[object]:
        """Return Twilio Events for one call.

        Twilio exposes these roughly 15 minutes after a call ends. The event
        objects are SDK resources; callers can inspect ``request``/``response``.
        """
        return list(self._client.calls(call_sid).events.list(limit=limit))


@lru_cache(maxsize=1)
def get_client() -> TwilioClient:
    """Return the process-wide TwilioClient (constructed lazily from env vars)."""
    return TwilioClient(
        account_sid=load_string_from_env("TWILIO_ACCOUNT_SID"),
        auth_token=load_string_from_env("TWILIO_AUTH_TOKEN"),
        from_number=load_config()["twilio_master_phone_number"],
    )
