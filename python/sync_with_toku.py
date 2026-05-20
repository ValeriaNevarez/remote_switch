"""Sync job: reconcile each device's ``is_payment_current`` with Toku.

For every device:
  * compute the client's payment-current state from Toku invoices,
  * if the operator hasn't pinned the device manually and action is needed,
    place a Twilio call to enable/disable the switch and email an operator
    notification (active automatic devices when payment status differs from
    Toku or ``enabled`` differs from ``is_payment_current``),
  * always persist the latest Toku-derived value back to Firebase.
"""

from __future__ import annotations

from collections import defaultdict
from datetime import date, timedelta
import logging
from typing import Callable, Protocol

from firebase_api import (
    DatabaseDevice,
    get_devices,
    update_device_enabled,
    update_device_payment_current,
)
from gmail_api import GmailClient, GmailMessage
from log_config import configure_logging, log_event
from repo_config import load_config
from switch_caller import get_switch_caller
from toku_api import (
    TokuCustomer,
    TokuInvoice,
    are_invoices_current,
    get_all_customers,
    get_invoices,
)

# Type aliases for the dependencies we inject. Notify/save are single-method
# behaviors, so plain callables read better than a Protocol per role.
NotifyStateChange = Callable[[DatabaseDevice, bool, bool], None]
UpdatePaymentCurrent = Callable[[str, bool], None]
UpdateDeviceEnabled = Callable[[str, bool], None]
_LOG_PREFIX = "sync"
_LOGGER = logging.getLogger(__name__)


class _SwitchOps(Protocol):
    """Just enough of :class:`switch_caller.SwitchCaller` for the syncer."""

    def call_switch_with_retries(
        self, phone_number: str, enabled: bool, *, max_retries: int
    ) -> tuple[str, bool]: ...


def _group_invoices_by_customer(
    invoices: list[TokuInvoice],
) -> dict[str, list[TokuInvoice]]:
    grouped: dict[str, list[TokuInvoice]] = defaultdict(list)
    for invoice in invoices:
        grouped[invoice.customer_id].append(invoice)
    return grouped


def _toku_payment_current_for(
    device: DatabaseDevice,
    customer_by_number: dict[str, TokuCustomer],
    invoices_by_customer: dict[str, list[TokuInvoice]],
    as_of_date: date,
) -> bool | None:
    """Toku's verdict for ``device``, or ``None`` if we can't make a determination
    (no client_number on the device, or no matching Toku customer).
    """
    if not device.client_number:
        return None
    customer = customer_by_number.get(device.client_number)
    if customer is None:
        return None
    invoices = invoices_by_customer.get(customer.customer_id, [])
    return are_invoices_current(invoices, as_of_date)


def _device_needs_sync_action(device: DatabaseDevice, toku_current: bool) -> bool:
    """Whether an active automatic device should be called during Toku sync."""
    if not device.is_active or device.is_manual_override:
        return False
    return (
        device.is_payment_current != toku_current
        or device.enabled != device.is_payment_current
    )


def _log(device: DatabaseDevice, *, event: str = "toku_sync", **fields: object) -> None:
    """Single-line, structured log for one device's sync outcome."""
    log_event(
        _LOGGER,
        prefix=_LOG_PREFIX,
        event=event,
        phone=device.phone_number,
        client=repr(device.client_name),
        **fields,
    )


class TokuSyncer:
    """Reconcile each device's ``is_payment_current`` with Toku.

    Collaborators (switch operations, notification sender, DB writer) are
    injected so tests can hand in stubs.
    """

    def __init__(
        self,
        switch_ops: _SwitchOps,
        notify_state_change: NotifyStateChange,
        update_payment_current: UpdatePaymentCurrent,
        update_enabled: UpdateDeviceEnabled,
        *,
        max_call_retries: int,
    ):
        self._switch_ops = switch_ops
        self._notify = notify_state_change
        self._save = update_payment_current
        self._update_enabled = update_enabled
        self._max_call_retries = max_call_retries

    def sync_device(
        self,
        device: DatabaseDevice,
        customer_by_number: dict[str, TokuCustomer],
        invoices_by_customer: dict[str, list[TokuInvoice]],
        *,
        as_of_date: date,
    ) -> None:
        toku_current = _toku_payment_current_for(
            device, customer_by_number, invoices_by_customer, as_of_date
        )
        if toku_current is None:
            _log(device, action="skip", reason="no_toku_data")
            return

        needs_action = _device_needs_sync_action(device, toku_current)
        if needs_action:
            _log(
                device,
                action="enable" if toku_current else "disable",
                toku_current=toku_current,
                db_current=device.is_payment_current,
            )
            _, call_succeeded = self._switch_ops.call_switch_with_retries(
                device.phone_number, toku_current, max_retries=self._max_call_retries
            )
            self._update_enabled(device.key, toku_current)
            self._notify(device, toku_current, call_succeeded)
            if not call_succeeded:
                _log(
                    device,
                    action="call_failed",
                    toku_current=toku_current,
                )
        else:
            _log(device, action="noop", toku_current=toku_current)

        self._save(device.key, toku_current)


def _make_gmail_notifier(
    gmail: GmailClient, from_email: str, to_email: str, cc_emails: str
) -> NotifyStateChange:
    """Production wiring of :data:`NotifyStateChange` backed by Gmail."""

    def notify(device: DatabaseDevice, enabled: bool, call_succeeded: bool) -> None:
        action = "habilitado" if enabled else "deshabilitado"
        client_name = device.client_name or "(sin nombre)"
        client_number = device.client_number or "-"
        if call_succeeded:
            call_outcome = (
                "<b>Llamadas:</b> exitosas (al menos un intento quedó como "
                "completado en Twilio)."
            )
        else:
            call_outcome = (
                "<b>Llamadas:</b> fallidas (ningún intento quedó como completado "
                "en Twilio; verificar el switch manualmente)."
            )
        body = f"""
        <p>El switch del cliente <b>{client_name}</b> (No. cliente: {client_number})
        fue <b>{action}</b> automáticamente por estado de pagos en Toku.</p>
        <p>{call_outcome}</p>
        """
        gmail.send_html_email(
            GmailMessage(
                to=to_email,
                from_email=from_email,
                cc=cc_emails,
                subject=f"[Switch remoto] {client_name}: {action}",
                html_body=body,
            )
        )

    return notify


def main() -> None:
    configure_logging()
    devices = get_devices()
    customers = get_all_customers()
    invoice_from_date = date.today() - timedelta(days=60)
    invoices = get_invoices(due_date_from=invoice_from_date)
    customer_by_number = {
        customer.customer_number: customer for customer in customers
    }
    invoices_by_customer = _group_invoices_by_customer(invoices)

    cfg = load_config()
    cutoff_date = date.today() - timedelta(days=cfg["toku_sync_grace_period_days"])
    syncer = TokuSyncer(
        switch_ops=get_switch_caller(),
        notify_state_change=_make_gmail_notifier(
            GmailClient(),
            cfg["from_email"],
            cfg["toku_sync_to_email"],
            cfg["toku_sync_cc_emails"],
        ),
        update_payment_current=update_device_payment_current,
        update_enabled=update_device_enabled,
        max_call_retries=cfg["toku_sync_max_call_retries"],
    )

    for device in devices:
        try:
            syncer.sync_device(
                device, customer_by_number, invoices_by_customer, as_of_date=cutoff_date
            )
        except Exception as e:
            _LOGGER.exception(
                "%s: event=toku_sync phone=%s client=%r action=error error=%r",
                _LOG_PREFIX,
                device.phone_number,
                device.client_name,
                e,
            )


if __name__ == "__main__":
    main()
