"""Explain Toku invoice and payment status for one customer by client number.

Fetches the matching Toku customer, invoices in the same window as sync, and
any Firebase devices with that ``client_number``. Prints invoice details and
why the client is or is not payment-current.

Run from repo root::

    python python/explain_customer_invoices.py 12345
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import date, timedelta
import sys

from firebase_api import DatabaseDevice, get_devices
from repo_config import load_config
from sync_with_toku import _INVOICE_FETCH_LOOKBACK_DAYS
from toku_api import TokuCustomer, TokuInvoice, are_invoices_current, get_all_customers, get_invoices

_DIVIDER = "=" * 72


@dataclass(frozen=True)
class InvoiceRow:
    invoice_id: str
    due_date: date
    is_paid: bool
    status: str
    detail: str


def _invoice_status(invoice: TokuInvoice, as_of_date: date) -> tuple[str, str]:
    if invoice.is_paid:
        return "paid", "Pagada"
    if invoice.due_date >= as_of_date:
        days_until_due = (invoice.due_date - as_of_date).days
        return "not_due", f"No vencida (vence en {days_until_due} días respecto al corte)"
    days_overdue = (as_of_date - invoice.due_date).days
    return "overdue", f"Vencida hace {days_overdue} días (corte {as_of_date})"


def _build_invoice_rows(invoices: list[TokuInvoice], as_of_date: date) -> list[InvoiceRow]:
    rows: list[InvoiceRow] = []
    for invoice in sorted(invoices, key=lambda inv: inv.due_date, reverse=True):
        status, detail = _invoice_status(invoice, as_of_date)
        rows.append(
            InvoiceRow(
                invoice_id=invoice.invoice_id,
                due_date=invoice.due_date,
                is_paid=invoice.is_paid,
                status=status,
                detail=detail,
            )
        )
    return rows


def _reason_not_current(invoices: list[TokuInvoice], as_of_date: date) -> tuple[str, str]:
    if not invoices:
        return (
            "sin_facturas_en_ventana",
            f"No hay facturas con vencimiento desde hace {_INVOICE_FETCH_LOOKBACK_DAYS} días.",
        )
    if not any(invoice.is_paid for invoice in invoices):
        return (
            "ninguna_pagada",
            "Hay facturas en la ventana, pero ninguna está marcada como pagada en Toku.",
        )
    overdue = [
        invoice
        for invoice in invoices
        if not invoice.is_paid and invoice.due_date < as_of_date
    ]
    if overdue:
        ids = ", ".join(inv.invoice_id for inv in sorted(overdue, key=lambda i: i.due_date))
        return (
            "factura_vencida_impaga",
            f"{len(overdue)} factura(s) impaga(s) con vencimiento anterior al corte: {ids}.",
        )
    return ("desconocido", "No se pudo determinar la causa (revisar lógica).")


def _format_bool(value: bool) -> str:
    return "sí" if value else "no"


def _devices_for_client(devices: list[DatabaseDevice], client_number: str) -> list[DatabaseDevice]:
    return [d for d in devices if d.client_number == client_number]


def _print_device(device: DatabaseDevice) -> None:
    print(f"  Dispositivo: {device.client_name or '(sin nombre)'}")
    print(f"    Teléfono: {device.phone_number}")
    print(f"    Serial: {device.serial_number}")
    print(f"    Firebase key: {device.key}")
    print(f"    is_payment_current: {_format_bool(device.is_payment_current)}")
    print(f"    enabled: {_format_bool(device.enabled)}")
    print(f"    is_active: {_format_bool(device.is_active)}")
    print(f"    is_manual_override: {_format_bool(device.is_manual_override)}")


def explain_customer(customer_number: str) -> int:
    cfg = load_config()
    today = date.today()
    grace_days = cfg["toku_sync_grace_period_days"]
    as_of_date = today - timedelta(days=grace_days)
    invoice_from = today - timedelta(days=_INVOICE_FETCH_LOOKBACK_DAYS)

    customers = get_all_customers()
    customer_by_number = {c.customer_number: c for c in customers}
    customer = customer_by_number.get(customer_number)
    if customer is None:
        print(f"No se encontró cliente en Toku con número {customer_number!r}.")
        print(f"Clientes en Toku: {len(customers)}")
        return 1

    invoices = get_invoices(customer_id=customer.customer_id, due_date_from=invoice_from)
    toku_current = are_invoices_current(invoices, as_of_date)
    invoice_rows = _build_invoice_rows(invoices, as_of_date)
    devices = _devices_for_client(get_devices(), customer_number)

    print(_DIVIDER)
    print(f"Cliente Toku: {customer_number!r}")
    print(f"  customer_id: {customer.customer_id}")
    print()
    print("Criterio (mismo que sync_with_toku / toku_api.are_invoices_current):")
    print(f"  Hoy: {today}")
    print(f"  Días de gracia: {grace_days}")
    print(f"  Fecha de corte (hoy - gracia): {as_of_date}")
    print(
        f"  Facturas: vencimiento desde {invoice_from} "
        f"({_INVOICE_FETCH_LOOKBACK_DAYS} días)"
    )
    print()
    print(f"Toku al corriente: {_format_bool(toku_current)}")
    if toku_current:
        if not invoices:
            print("  Motivo: sin facturas en la ventana (se considera al corriente).")
        else:
            print("  Motivo: al menos una factura pagada y ninguna impaga vencida.")
    else:
        short, detail = _reason_not_current(invoices, as_of_date)
        print(f"  Motivo: {short}")
        print(f"  Detalle: {detail}")
    print()

    if invoice_rows:
        print(f"Facturas ({len(invoice_rows)}):")
        print(f"  {'ID':<28} {'Vence':<12} {'Pagada':<8} {'Estado':<10} Notas")
        for row in invoice_rows:
            paid = _format_bool(row.is_paid)
            print(
                f"  {row.invoice_id:<28} {row.due_date!s:<12} {paid:<8} "
                f"{row.status:<10} {row.detail}"
            )
    else:
        print("Facturas: (ninguna en la ventana)")
    print()

    if devices:
        print(f"Dispositivos en Firebase con # Cliente = {customer_number!r}: {len(devices)}")
        for device in devices:
            print()
            _print_device(device)
            if device.is_payment_current != toku_current:
                print(
                    "    AVISO: is_payment_current en Firebase difiere de Toku "
                    "(se actualizará en el próximo sync)."
                )
    else:
        print(f"Dispositivos en Firebase con # Cliente = {customer_number!r}: ninguno")

    print(_DIVIDER)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Explain Toku invoice and payment status for one client number."
    )
    parser.add_argument(
        "customer_number",
        help="Client number (# Cliente) as stored in Firebase and Toku metadata",
    )
    args = parser.parse_args()
    customer_number = args.customer_number.strip()
    if not customer_number:
        parser.error("customer_number must not be empty")
    return explain_customer(customer_number)


if __name__ == "__main__":
    sys.exit(main())
