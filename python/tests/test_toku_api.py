"""Unit tests for parsing and payment logic in ``toku_api``."""

from __future__ import annotations

import sys
import unittest
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from toku_api import (
    TokuClient,
    TokuCustomer,
    TokuInvoice,
    are_invoices_current,
    customer_for_invoice_lookup,
)


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


class TestParseCustomer(unittest.TestCase):
    def test_parses_quien_paga_from_metadata(self) -> None:
        customer = TokuClient._parse_customer(
            {
                "id": "cust-1",
                "metadata": {"Numero": "635", "quien_paga": "123"},
            }
        )
        self.assertIsNotNone(customer)
        assert customer is not None
        self.assertEqual(customer.customer_number, "635")
        self.assertEqual(customer.payer_number, "123")

    def test_empty_quien_paga_is_none(self) -> None:
        customer = TokuClient._parse_customer(
            {
                "id": "cust-1",
                "metadata": {"Numero": "635", "quien_paga": ""},
            }
        )
        self.assertIsNotNone(customer)
        assert customer is not None
        self.assertIsNone(customer.payer_number)


class TestCustomerForInvoiceLookup(unittest.TestCase):
    def test_uses_payer_when_quien_paga_is_valid(self) -> None:
        client = TokuCustomer("cust-a", "635", payer_number="123")
        payer = TokuCustomer("cust-b", "123")
        by_number = {"635": client, "123": payer}
        self.assertIs(customer_for_invoice_lookup(client, by_number), payer)

    def test_uses_self_when_quien_paga_missing(self) -> None:
        client = TokuCustomer("cust-a", "635")
        by_number = {"635": client}
        self.assertIs(customer_for_invoice_lookup(client, by_number), client)

    def test_uses_self_when_quien_paga_unknown(self) -> None:
        client = TokuCustomer("cust-a", "635", payer_number="999")
        by_number = {"635": client}
        self.assertIs(customer_for_invoice_lookup(client, by_number), client)

    def test_does_not_follow_payers_quien_paga(self) -> None:
        client = TokuCustomer("cust-a", "635", payer_number="123")
        payer = TokuCustomer("cust-b", "123", payer_number="456")
        grandparent = TokuCustomer("cust-c", "456")
        by_number = {"635": client, "123": payer, "456": grandparent}
        self.assertIs(customer_for_invoice_lookup(client, by_number), payer)


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

    def test_returns_false_when_none_are_paid(self) -> None:
        invoices = [
            TokuInvoice("a", "cust-1", date(2026, 5, 1), False),
            TokuInvoice("b", "cust-1", date(2026, 6, 1), False),
        ]
        self.assertFalse(are_invoices_current(invoices, as_of_date=date(2026, 4, 1)))

    def test_returns_true_when_invoice_list_is_empty(self) -> None:
        self.assertTrue(are_invoices_current([], as_of_date=date(2026, 4, 1)))


if __name__ == "__main__":
    unittest.main()
