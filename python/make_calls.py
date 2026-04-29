"""Daily job: place a call to each active switch that needs one."""

from __future__ import annotations

import logging
import time
from datetime import datetime, timezone
from typing import Callable, Iterable, Iterator, Protocol

from firebase_api import DatabaseDevice, get_devices
from log_config import configure_logging, log_event
from switch_caller import POST_MASTER_CHANGE_SLEEP_SECONDS, get_switch_caller
from twilio_api import LastCallStatus
from twilio_api import get_client as get_twilio_client

DAYS_BETWEEN_CALLS = 20
_LOG_PREFIX = "scheduler"
_LOGGER = logging.getLogger(__name__)


class _CallStatusProvider(Protocol):
    """Just enough of :class:`twilio_api.TwilioClient` for scheduling decisions."""

    def get_last_call_status(self, phone_number: str) -> LastCallStatus | None: ...


class _SwitchOps(Protocol):
    """Just enough of :class:`switch_caller.SwitchCaller` for the orchestration."""

    def call_switch(self, phone_number: str, enabled: bool) -> str: ...
    def change_master(self, phone_number: str) -> str: ...


def _days_since(dt: datetime | None) -> int | None:
    if dt is None:
        return None
    return (datetime.now(timezone.utc) - dt).days


def _effective_enabled(device: DatabaseDevice) -> bool:
    """The state we want the switch in.

    If the operator has pinned the device manually, honor ``device.enabled``.
    Otherwise the switch should reflect the client's Toku payment status.
    """
    return device.enabled if device.is_manual_override else device.is_payment_current


def _iter_callable(
    devices: Iterable[DatabaseDevice], *, only_active: bool
) -> Iterator[tuple[str, bool]]:
    """Yield ``(phone_number, enabled)`` for devices we can call."""
    for device in devices:
        if only_active and not device.is_active:
            continue
        if not device.phone_number:
            continue
        yield device.phone_number, _effective_enabled(device)


def _log_call_decision(
    phone: str, enabled: bool, reason: str, **context: object
) -> None:
    """Single-line, structured log for call-scheduler decisions."""
    log_event(
        _LOGGER,
        prefix=_LOG_PREFIX,
        event="call_decision",
        phone=phone,
        enabled=enabled,
        reason=reason,
        **context,
    )


def _log_call_error(phone: str, enabled: bool, error: Exception) -> None:
    """Single-line, structured log for per-device scheduler failures."""
    _LOGGER.exception(
        "%s: event=call_error phone=%s enabled=%s error=%r",
        _LOG_PREFIX,
        phone,
        enabled,
        error,
    )


class CallScheduler:
    """Decides which devices to call and drives the calls via injected services."""

    def __init__(
        self,
        twilio: _CallStatusProvider,
        switch_ops: _SwitchOps,
        *,
        sleep: Callable[[float], None] = time.sleep,
        days_between_calls: int = DAYS_BETWEEN_CALLS,
    ):
        self._twilio = twilio
        self._switch_ops = switch_ops
        self._sleep = sleep
        self._days_between_calls = days_between_calls

    def call_numbers_that_need_it(self, devices: list[DatabaseDevice]) -> None:
        for phone, enabled in _iter_callable(devices, only_active=True):
            try:
                last_call = self._twilio.get_last_call_status(phone)

                if last_call is None:
                    _log_call_decision(phone, enabled, reason="no_prior_call")
                    self._switch_ops.change_master(phone)
                    self._sleep(POST_MASTER_CHANGE_SLEEP_SECONDS)
                    self._switch_ops.call_switch(phone, enabled)
                    continue

                if last_call.status != "completed":
                    _log_call_decision(
                        phone, enabled,
                        reason="last_call_not_completed",
                        last_status=last_call.status,
                    )
                    self._switch_ops.call_switch(phone, enabled)
                    continue

                days_since_call = _days_since(last_call.date)
                if days_since_call is not None and days_since_call > self._days_between_calls:
                    _log_call_decision(
                        phone, enabled,
                        reason="stale_completed_call",
                        days_since=days_since_call,
                    )
                    self._switch_ops.call_switch(phone, enabled)
            except Exception as exc:
                _log_call_error(phone, enabled, exc)


def main() -> None:
    configure_logging()
    devices = get_devices()
    scheduler = CallScheduler(
        twilio=get_twilio_client(),
        switch_ops=get_switch_caller(),
    )
    scheduler.call_numbers_that_need_it(devices)


if __name__ == "__main__":
    main()
