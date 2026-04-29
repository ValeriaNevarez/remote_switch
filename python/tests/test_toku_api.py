"""Unit tests for parsing and payment logic in ``toku_api``."""

from __future__ import annotations

import sys
import unittest
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from toku_api import TokuClient, TokuInvoice, are_invoices_current


class TestParseInvoice(unittest.TestCase):
    def test_accepts_boolean_is_paid(self) -> None:
        invoice = TokuClient._parse_invoice(
            {
                "id": "inv-1",
                "customer": "cust-1",
                "due_date": "2026-04-01",
                "is_paid": False,
            }
        )
        self.assertIsNotNone(invoice)
        self.assertFalse(invoice.is_paid)

    def test_accepts_string_false_is_paid(self) -> None:
        invoice = TokuClient._parse_invoice(
            {
                "id": "inv-1",
                "customer": "cust-1",
                "due_date": "2026-04-01",
                "is_paid": "false",
            }
        )
        self.assertIsNotNone(invoice)
        self.assertFalse(invoice.is_paid)

    def test_rejects_unparseable_is_paid(self) -> None:
        invoice = TokuClient._parse_invoice(
            {
                "id": "inv-1",
                "customer": "cust-1",
                "due_date": "2026-04-01",
                "is_paid": "yes",
            }
        )
        self.assertIsNone(invoice)


class TestAreInvoicesCurrent(unittest.TestCase):
    def test_returns_false_when_overdue_unpaid_exists(self) -> None:
        invoices = [
            TokuInvoice("a", "cust-1", date(2026, 1, 1), False),
            TokuInvoice("b", "cust-1", date(2026, 5, 1), True),
        ]
        self.assertFalse(are_invoices_current(invoices, as_of_date=date(2026, 4, 1)))

    def test_returns_true_when_all_paid_or_not_due(self) -> None:
        invoices = [
            TokuInvoice("a", "cust-1", date(2026, 5, 1), False),
            TokuInvoice("b", "cust-1", date(2026, 1, 1), True),
        ]
        self.assertTrue(are_invoices_current(invoices, as_of_date=date(2026, 4, 1)))


if __name__ == "__main__":
    unittest.main()
