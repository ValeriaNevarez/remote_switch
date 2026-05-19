"""Test doubles for the API-client protocols used by the orchestrators.

Each fake records the calls it received so a test can ``assert`` against them,
and only implements the subset of the real client surface that the
orchestration code actually uses (matching the ``Protocol`` definitions in
``make_calls`` and ``sync_with_toku``).
"""

from __future__ import annotations

from firebase_api import DatabaseDevice
from twilio_api import LastCallStatus


class FakeTwilio:
    """Implements :class:`make_calls._CallStatusProvider`."""

    def __init__(self, statuses: dict[str, LastCallStatus] | None = None):
        self.queries: list[str] = []
        self._statuses: dict[str, LastCallStatus] = statuses or {}

    def set_status(self, phone_number: str, status: LastCallStatus) -> None:
        self._statuses[phone_number] = status

    def get_last_call_status(self, phone_number: str) -> LastCallStatus | None:
        self.queries.append(phone_number)
        return self._statuses.get(phone_number)


class FakeSwitchOps:
    """Implements :class:`make_calls._SwitchOps` and :class:`sync_with_toku._SwitchOps`."""

    def __init__(self) -> None:
        self.calls: list[tuple[str, bool]] = []
        self.master_changes: list[str] = []
        self._call_succeeded: dict[str, bool] = {}

    def call_switch(self, phone_number: str, enabled: bool) -> str:
        self.calls.append((phone_number, enabled))
        return f"sid-call-{len(self.calls)}"

    def call_switch_with_retries(
        self, phone_number: str, enabled: bool, *, max_retries: int
    ) -> tuple[str, bool]:
        sid = self.call_switch(phone_number, enabled)
        return sid, self._call_succeeded.get(phone_number, True)

    def set_call_succeeded(self, phone_number: str, succeeded: bool) -> None:
        self._call_succeeded[phone_number] = succeeded

    def change_master(self, phone_number: str) -> str:
        self.master_changes.append(phone_number)
        return f"sid-msg-{len(self.master_changes)}"


class RecordingSleep:
    """Drop-in replacement for ``time.sleep`` that records every duration."""

    def __init__(self) -> None:
        self.durations: list[float] = []

    def __call__(self, seconds: float) -> None:
        self.durations.append(seconds)


class RecordingNotifier:
    """Callable conforming to :data:`sync_with_toku.NotifyStateChange`."""

    def __init__(self) -> None:
        self.notifications: list[tuple[str, bool, bool]] = []

    def __call__(
        self, device: DatabaseDevice, enabled: bool, call_succeeded: bool
    ) -> None:
        self.notifications.append((device.key, enabled, call_succeeded))


class RecordingDeviceWriter:
    """Callable conforming to :data:`sync_with_toku.UpdatePaymentCurrent`."""

    def __init__(self) -> None:
        self.writes: list[tuple[str, bool]] = []

    def __call__(self, key: str, is_payment_current: bool) -> None:
        self.writes.append((key, is_payment_current))


class RecordingEnabledWriter:
    """Callable conforming to :data:`sync_with_toku.UpdateDeviceEnabled`."""

    def __init__(self) -> None:
        self.writes: list[tuple[str, bool]] = []

    def __call__(self, key: str, enabled: bool) -> None:
        self.writes.append((key, enabled))


def make_device(**overrides: object) -> DatabaseDevice:
    """Build a fully-populated DatabaseDevice with sensible defaults for tests."""
    base: dict[str, object] = dict(
        serial_number="1",
        phone_number="+5215555555555",
        enabled=True,
        is_active=True,
        client_name="Acme Corp",
        client_number="100",
        is_manual_override=False,
        is_payment_current=True,
        key="dev-1",
    )
    base.update(overrides)
    return DatabaseDevice(**base)  # type: ignore[arg-type]
