"""Unit tests for ``make_calls.CallScheduler``."""

from __future__ import annotations

import sys
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from make_calls import CallScheduler
from switch_caller import POST_MASTER_CHANGE_SLEEP_SECONDS
from twilio_api import LastCallStatus

from tests.fakes import FakeSwitchOps, FakeTwilio, RecordingSleep, make_device


def _now() -> datetime:
    return datetime.now(timezone.utc)


class TestIterCallable(unittest.TestCase):
    """Sanity-checks for the device filter shared by all CallScheduler methods."""

    def setUp(self) -> None:
        self.twilio = FakeTwilio()
        self.switch_ops = FakeSwitchOps()
        self.sleep = RecordingSleep()
        self.scheduler = CallScheduler(
            twilio=self.twilio,
            switch_ops=self.switch_ops,
            sleep=self.sleep,
        )


class TestCallNumbersThatNeedIt(unittest.TestCase):
    """The decision tree in CallScheduler.call_numbers_that_need_it."""

    def setUp(self) -> None:
        self.twilio = FakeTwilio()
        self.switch_ops = FakeSwitchOps()
        self.sleep = RecordingSleep()
        self.scheduler = CallScheduler(
            twilio=self.twilio,
            switch_ops=self.switch_ops,
            sleep=self.sleep,
            days_between_calls=20,
        )

    def test_no_prior_call_changes_master_then_sleeps_then_calls(self) -> None:
        device = make_device(phone_number="+1")
        # Note: FakeTwilio returns None for unseen phones, simulating "no record".
        self.scheduler.call_numbers_that_need_it([device])

        self.assertEqual(self.switch_ops.master_changes, ["+1"])
        self.assertEqual(self.sleep.durations, [POST_MASTER_CHANGE_SLEEP_SECONDS])
        self.assertEqual(self.switch_ops.calls, [("+1", True)])

    def test_last_call_not_completed_calls_without_master_change(self) -> None:
        # is_payment_current=False, override=False -> effective enabled = False
        device = make_device(phone_number="+1", is_payment_current=False)
        self.twilio.set_status("+1", LastCallStatus(status="busy", date=_now()))

        self.scheduler.call_numbers_that_need_it([device])

        self.assertEqual(self.switch_ops.master_changes, [])
        self.assertEqual(self.sleep.durations, [])
        self.assertEqual(self.switch_ops.calls, [("+1", False)])

    def test_recent_completed_call_skipped(self) -> None:
        device = make_device(phone_number="+1")
        self.twilio.set_status(
            "+1", LastCallStatus(status="completed", date=_now() - timedelta(days=5))
        )

        self.scheduler.call_numbers_that_need_it([device])

        self.assertEqual(self.switch_ops.calls, [])
        self.assertEqual(self.switch_ops.master_changes, [])
        self.assertEqual(self.sleep.durations, [])

    def test_stale_completed_call_triggers_call(self) -> None:
        device = make_device(phone_number="+1")
        self.twilio.set_status(
            "+1", LastCallStatus(status="completed", date=_now() - timedelta(days=30))
        )

        self.scheduler.call_numbers_that_need_it([device])

        self.assertEqual(self.switch_ops.calls, [("+1", True)])
        self.assertEqual(self.switch_ops.master_changes, [])

    def test_threshold_is_configurable(self) -> None:
        """``days_between_calls`` is injected; tests can shrink it to 1 day."""
        scheduler = CallScheduler(
            twilio=self.twilio,
            switch_ops=self.switch_ops,
            sleep=self.sleep,
            days_between_calls=1,
        )
        device = make_device(phone_number="+1")
        self.twilio.set_status(
            "+1", LastCallStatus(status="completed", date=_now() - timedelta(days=2))
        )

        scheduler.call_numbers_that_need_it([device])

        self.assertEqual(self.switch_ops.calls, [("+1", True)])

    def test_inactive_devices_are_never_called_by_need_it_path(self) -> None:
        device = make_device(phone_number="+1", is_active=False)
        self.scheduler.call_numbers_that_need_it([device])
        self.assertEqual(self.switch_ops.calls, [])
        self.assertEqual(self.twilio.queries, [])  # never even queried Twilio

    def test_call_failure_for_one_device_does_not_stop_following_devices(self) -> None:
        class ExplodingSwitchOps(FakeSwitchOps):
            def call_switch(self, phone_number: str, enabled: bool) -> str:
                if phone_number == "+1":
                    raise RuntimeError("twilio down")
                return super().call_switch(phone_number, enabled)

        switch_ops = ExplodingSwitchOps()
        scheduler = CallScheduler(
            twilio=self.twilio,
            switch_ops=switch_ops,
            sleep=self.sleep,
            days_between_calls=20,
        )
        self.twilio.set_status("+1", LastCallStatus(status="busy", date=_now()))
        self.twilio.set_status("+2", LastCallStatus(status="busy", date=_now()))

        scheduler.call_numbers_that_need_it(
            [
                make_device(phone_number="+1"),
                make_device(phone_number="+2", key="dev-2"),
            ]
        )

        self.assertEqual(switch_ops.calls, [("+2", True)])


class TestEffectiveEnabledRule(unittest.TestCase):
    """The ``enabled`` value passed to call_switch follows ``_effective_enabled``:

      * if ``is_manual_override`` -> use ``enabled``
      * else                      -> use ``is_payment_current``
    """

    def setUp(self) -> None:
        self.twilio = FakeTwilio()
        self.switch_ops = FakeSwitchOps()
        self.scheduler = CallScheduler(
            twilio=self.twilio,
            switch_ops=self.switch_ops,
            sleep=RecordingSleep(),
        )

    def _call_one(self, **device_overrides: object) -> tuple[str, bool]:
        device = make_device(phone_number="+1", **device_overrides)
        # Seed a non-completed status so we hit the straight "call_switch" branch
        # (no master change, no sleep) and can read the enabled value directly.
        self.twilio.set_status("+1", LastCallStatus(status="busy", date=_now()))
        self.scheduler.call_numbers_that_need_it([device])
        self.assertEqual(len(self.switch_ops.calls), 1)
        return self.switch_ops.calls[0]

    def test_manual_override_on_uses_enabled_field(self) -> None:
        # override wins: is_payment_current is ignored entirely.
        self.assertEqual(
            self._call_one(is_manual_override=True, enabled=False, is_payment_current=True),
            ("+1", False),
        )

    def test_manual_override_on_uses_enabled_field_when_true(self) -> None:
        self.assertEqual(
            self._call_one(is_manual_override=True, enabled=True, is_payment_current=False),
            ("+1", True),
        )

    def test_manual_override_off_uses_payment_current_field(self) -> None:
        # override off: enabled is ignored, we follow Toku's verdict.
        self.assertEqual(
            self._call_one(is_manual_override=False, enabled=True, is_payment_current=False),
            ("+1", False),
        )

    def test_manual_override_off_uses_payment_current_field_when_true(self) -> None:
        self.assertEqual(
            self._call_one(is_manual_override=False, enabled=False, is_payment_current=True),
            ("+1", True),
        )


if __name__ == "__main__":
    unittest.main()
