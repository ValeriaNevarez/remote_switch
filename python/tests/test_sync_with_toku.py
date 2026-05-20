"""Unit tests for ``sync_with_toku.TokuSyncer``."""

from __future__ import annotations

import sys
import unittest
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sync_with_toku import TokuSyncer, _device_needs_sync_action, _group_invoices_by_customer
from toku_api import TokuCustomer, TokuInvoice

from tests.fakes import (
    FakeSwitchOps,
    RecordingDeviceWriter,
    RecordingEnabledWriter,
    RecordingNotifier,
    make_device,
)


class TestGroupInvoicesByCustomer(unittest.TestCase):
    def test_groups_by_customer_id(self) -> None:
        invoices = [
            TokuInvoice("a", "cust-1", date(2026, 4, 1), False),
            TokuInvoice("b", "cust-1", date(2026, 5, 1), True),
            TokuInvoice("c", "cust-2", date(2026, 5, 1), True),
        ]
        grouped = _group_invoices_by_customer(invoices)
        self.assertEqual(set(grouped), {"cust-1", "cust-2"})
        self.assertEqual(len(grouped["cust-1"]), 2)
        self.assertEqual(len(grouped["cust-2"]), 1)

    def test_empty_input_returns_empty_mapping(self) -> None:
        self.assertEqual(_group_invoices_by_customer([]), {})


class TestTokuSyncer(unittest.TestCase):
    """The decision matrix in TokuSyncer.sync_device."""

    def setUp(self) -> None:
        self.switch_ops = FakeSwitchOps()
        self.notifier = RecordingNotifier()
        self.writer = RecordingDeviceWriter()
        self.enabled_writer = RecordingEnabledWriter()
        self.syncer = TokuSyncer(
            switch_ops=self.switch_ops,
            notify_state_change=self.notifier,
            update_payment_current=self.writer,
            update_enabled=self.enabled_writer,
            max_call_retries=2,
        )
        self.customer_by_number = {"100": TokuCustomer("cust-1", "100")}
        self.today = date(2026, 4, 27)

    def _invoices(self, *, paid: bool) -> dict[str, list[TokuInvoice]]:
        return {
            "cust-1": [TokuInvoice("inv-1", "cust-1", date(2026, 1, 1), paid)],
        }

    def _sync(
        self,
        device,
        invoices_by_customer: dict[str, list[TokuInvoice]],
    ) -> None:
        self.syncer.sync_device(
            device,
            self.customer_by_number,
            invoices_by_customer,
            as_of_date=self.today,
        )

    # --- "do nothing" branches ------------------------------------------

    def test_manual_override_skips_call_and_email_but_still_saves(self) -> None:
        device = make_device(is_manual_override=True, is_payment_current=True)
        self._sync(device, self._invoices(paid=False))

        self.assertEqual(self.switch_ops.calls, [])
        self.assertEqual(self.notifier.notifications, [])
        self.assertEqual(self.enabled_writer.writes, [])
        self.assertEqual(self.writer.writes, [("dev-1", False)])

    def test_db_and_toku_already_agree_no_action_just_save(self) -> None:
        device = make_device(is_payment_current=True)
        self._sync(device, self._invoices(paid=True))

        self.assertEqual(self.switch_ops.calls, [])
        self.assertEqual(self.notifier.notifications, [])
        self.assertEqual(self.enabled_writer.writes, [])
        self.assertEqual(self.writer.writes, [("dev-1", True)])

    def test_no_invoices_in_toku_marks_current(self) -> None:
        device = make_device(is_payment_current=False)
        self._sync(device, {})

        self.assertEqual(self.switch_ops.calls, [(device.phone_number, True)])
        self.assertEqual(self.writer.writes, [("dev-1", True)])

    # --- "act" branches -------------------------------------------------

    def test_db_says_current_but_toku_says_overdue_disables(self) -> None:
        device = make_device(
            phone_number="+1", is_manual_override=False, is_payment_current=True
        )
        self._sync(device, self._invoices(paid=False))

        self.assertEqual(self.switch_ops.calls, [("+1", False)])
        self.assertEqual(self.notifier.notifications, [("dev-1", False, True)])
        self.assertEqual(self.enabled_writer.writes, [("dev-1", False)])
        self.assertEqual(self.writer.writes, [("dev-1", False)])

    def test_db_says_overdue_but_toku_says_current_enables(self) -> None:
        device = make_device(
            phone_number="+1", is_manual_override=False, is_payment_current=False
        )
        self._sync(device, self._invoices(paid=True))

        self.assertEqual(self.switch_ops.calls, [("+1", True)])
        self.assertEqual(self.notifier.notifications, [("dev-1", True, True)])
        self.assertEqual(self.enabled_writer.writes, [("dev-1", True)])
        self.assertEqual(self.writer.writes, [("dev-1", True)])

    def test_active_automatic_enabled_mismatch_calls_even_when_toku_matches_payment(
        self,
    ) -> None:
        device = make_device(
            phone_number="+1",
            is_active=True,
            is_manual_override=False,
            enabled=True,
            is_payment_current=False,
        )
        self._sync(device, self._invoices(paid=False))

        self.assertEqual(self.switch_ops.calls, [("+1", False)])
        self.assertEqual(self.enabled_writer.writes, [("dev-1", False)])
        self.assertEqual(self.writer.writes, [("dev-1", False)])

    def test_inactive_enabled_mismatch_does_not_call(self) -> None:
        device = make_device(
            is_active=False,
            is_manual_override=False,
            enabled=True,
            is_payment_current=False,
        )
        self._sync(device, self._invoices(paid=True))

        self.assertEqual(self.switch_ops.calls, [])
        self.assertEqual(self.enabled_writer.writes, [])
        self.assertEqual(self.writer.writes, [("dev-1", True)])

    def test_failed_call_still_updates_enabled(self) -> None:
        device = make_device(
            phone_number="+1", is_manual_override=False, is_payment_current=True
        )
        self.switch_ops.set_call_succeeded("+1", False)
        self._sync(device, self._invoices(paid=False))

        self.assertEqual(self.notifier.notifications, [("dev-1", False, False)])
        self.assertEqual(self.enabled_writer.writes, [("dev-1", False)])
        self.assertEqual(self.writer.writes, [("dev-1", False)])

    # --- "skip entirely" branches (no Toku data) ------------------------

    def test_no_matching_toku_customer_skipped_no_save(self) -> None:
        device = make_device(client_number="999")  # not in customer_by_number
        self._sync(device, self._invoices(paid=True))

        self.assertEqual(self.switch_ops.calls, [])
        self.assertEqual(self.notifier.notifications, [])
        self.assertEqual(self.enabled_writer.writes, [])
        self.assertEqual(self.writer.writes, [])

    def test_blank_client_number_skipped_no_save(self) -> None:
        device = make_device(client_number="")
        self._sync(device, self._invoices(paid=True))

        self.assertEqual(self.switch_ops.calls, [])
        self.assertEqual(self.notifier.notifications, [])
        self.assertEqual(self.enabled_writer.writes, [])
        self.assertEqual(self.writer.writes, [])

    # --- ordering: notify only fires after the call -----------------------

    def test_call_failure_prevents_notify_and_save(self) -> None:
        """If switch_ops.call_switch_with_retries raises, we don't email or persist."""
        class ExplodingSwitchOps:
            def call_switch_with_retries(self, phone_number, enabled, *, max_retries):
                raise RuntimeError("twilio down")

        syncer = TokuSyncer(
            switch_ops=ExplodingSwitchOps(),
            notify_state_change=self.notifier,
            update_payment_current=self.writer,
            update_enabled=self.enabled_writer,
            max_call_retries=2,
        )
        device = make_device(is_payment_current=True)

        with self.assertRaises(RuntimeError):
            syncer.sync_device(
                device,
                self.customer_by_number,
                self._invoices(paid=False),
                as_of_date=self.today,
            )

        self.assertEqual(self.notifier.notifications, [])
        self.assertEqual(self.enabled_writer.writes, [])
        self.assertEqual(self.writer.writes, [])


class TestDeviceNeedsSyncAction(unittest.TestCase):
    def test_manual_override_never_needs_action(self) -> None:
        device = make_device(is_manual_override=True, enabled=True, is_payment_current=False)
        self.assertFalse(_device_needs_sync_action(device, toku_current=False))

    def test_inactive_never_needs_action(self) -> None:
        device = make_device(is_active=False, enabled=True, is_payment_current=False)
        self.assertFalse(_device_needs_sync_action(device, toku_current=True))

    def test_active_needs_action_when_enabled_differs_from_payment_current(self) -> None:
        device = make_device(is_active=True, enabled=True, is_payment_current=False)
        self.assertTrue(_device_needs_sync_action(device, toku_current=False))


if __name__ == "__main__":
    unittest.main()
