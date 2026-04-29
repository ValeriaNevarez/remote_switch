"""Wrapper around the Toku REST API (https://toku.readme.io/reference/introduccion)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from functools import lru_cache
import logging
from typing import Any, Callable, TypeVar

import requests

T = TypeVar("T")

from env import load_string_from_env
from log_config import configure_logging, log_event

BASE_URL = "https://api.trytoku.com"
CUSTOMERS_PATH = "/customers"
INVOICES_PATH = "/invoices"
DEFAULT_PAGE_SIZE = 50
REQUEST_TIMEOUT_SECONDS = 30
_LOG_PREFIX = "toku_api"
_LOGGER = logging.getLogger(__name__)


def _parse_optional_bool(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized == "true":
            return True
        if normalized == "false":
            return False
    return None


@dataclass(frozen=True)
class TokuCustomer:
    customer_id: str
    customer_number: str


@dataclass(frozen=True)
class TokuInvoice:
    invoice_id: str
    customer_id: str
    due_date: date
    is_paid: bool


class TokuClient:
    def __init__(self, api_token: str, base_url: str = BASE_URL):
        self._base_url = base_url.rstrip("/")
        self._session = requests.Session()
        self._session.headers.update(
            {
                "accept": "application/json",
                "x-api-key": api_token,
            }
        )

    # --- transport -------------------------------------------------------

    def _get(self, path: str, params: dict[str, Any]) -> dict[str, Any]:
        response = self._session.get(
            f"{self._base_url}{path}",
            params=params,
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        payload = response.json()
        if not isinstance(payload, dict):
            raise RuntimeError("Unexpected Toku response type: expected JSON object.")
        return payload

    @staticmethod
    def _extract_items(payload: dict[str, Any]) -> list[dict[str, Any]]:
        items = payload.get("items")
        if isinstance(items, list):
            return [item for item in items if isinstance(item, dict)]
        return []

    def _paginate(
        self,
        *,
        path: str,
        params: dict[str, Any],
        parse_item: Callable[[dict[str, Any]], T | None],
        record_label: str,
    ) -> list[T]:
        """Iterate every page at ``path``, parse items, and drop unparseable rows."""
        results: list[T] = []
        next_cursor: str | None = None
        page = 1
        while True:
            page_params = dict(params)
            if next_cursor:
                page_params["next_cursor"] = next_cursor
            payload = self._get(path, page_params)
            items = self._extract_items(payload)
            log_event(
                _LOGGER,
                prefix=_LOG_PREFIX,
                event="page_fetched",
                page=page,
                record_label=record_label,
                record_count=len(items),
            )
            for item in items:
                parsed = parse_item(item)
                if parsed is not None:
                    results.append(parsed)
            raw_cursor = payload.get("next_cursor")
            next_cursor = str(raw_cursor) if raw_cursor else None
            if next_cursor is None:
                return results
            page += 1

    # --- formatters / parsers --------------------------------------------

    @staticmethod
    def _format_date(value: date) -> str:
        return value.strftime("%Y-%m-%d")

    @staticmethod
    def _parse_customer(item: dict[str, Any]) -> TokuCustomer | None:
        customer_id = item.get("id")
        metadata = item.get("metadata") if isinstance(item.get("metadata"), dict) else {}
        customer_number = (
            item.get("number")
            or item.get("customer_number")
            or metadata.get("Numero")
            or metadata.get("numero")
        )
        if not customer_id or not customer_number:
            return None
        return TokuCustomer(
            customer_id=str(customer_id),
            customer_number=str(customer_number),
        )

    @staticmethod
    def _parse_invoice(item: dict[str, Any]) -> TokuInvoice | None:
        invoice_id = item.get("id")
        # Toku returns the customer reference under "customer" (a string id).
        # Accept "customer_id" too for forward-compatibility.
        customer_id = item.get("customer") or item.get("customer_id")
        due_date_raw = item.get("due_date")
        is_paid_raw = item.get("is_paid")
        is_paid = _parse_optional_bool(is_paid_raw)
        if not invoice_id or not customer_id or not due_date_raw or is_paid is None:
            return None
        try:
            due_date_value = date.fromisoformat(str(due_date_raw))
        except ValueError:
            return None
        return TokuInvoice(
            invoice_id=str(invoice_id),
            customer_id=str(customer_id),
            due_date=due_date_value,
            is_paid=is_paid,
        )

    # --- public API ------------------------------------------------------

    def get_all_customers(self, page_size: int = DEFAULT_PAGE_SIZE) -> list[TokuCustomer]:
        return self._paginate(
            path=CUSTOMERS_PATH,
            params={"page_size": page_size},
            parse_item=self._parse_customer,
            record_label="customer",
        )

    def get_invoices(
        self,
        *,
        customer_id: str | None = None,
        due_date_from: date | None = None,
        page_size: int = DEFAULT_PAGE_SIZE,
    ) -> list[TokuInvoice]:
        params: dict[str, Any] = {"page_size": page_size}
        if customer_id:
            params["customer_id"] = customer_id
        if due_date_from:
            params["due_date_from"] = self._format_date(due_date_from)
        return self._paginate(
            path=INVOICES_PATH,
            params=params,
            parse_item=self._parse_invoice,
            record_label="invoice",
        )


@lru_cache(maxsize=1)
def get_client() -> TokuClient:
    return TokuClient(api_token=load_string_from_env("TOKU_API_TOKEN"))


def get_all_customers() -> list[TokuCustomer]:
    return get_client().get_all_customers()


def get_invoices(
    *,
    customer_id: str | None = None,
    due_date_from: date | None = None,
    page_size: int = DEFAULT_PAGE_SIZE,
) -> list[TokuInvoice]:
    return get_client().get_invoices(
        customer_id=customer_id,
        due_date_from=due_date_from,
        page_size=page_size,
    )


def are_invoices_current(invoices: list[TokuInvoice], as_of_date: date) -> bool:
    return all(invoice.is_paid or invoice.due_date >= as_of_date for invoice in invoices)


def main() -> None:
    configure_logging()
    invoices = get_invoices(due_date_from=date(2026, 3, 1))
    log_event(_LOGGER, prefix=_LOG_PREFIX, event="invoices_parsed", count=len(invoices))
    for invoice in invoices:
        _LOGGER.info("%s: event=invoice value=%r", _LOG_PREFIX, invoice)

    invoices_current = are_invoices_current(invoices, date.today())
    log_event(
        _LOGGER,
        prefix=_LOG_PREFIX,
        event="invoices_current",
        value=invoices_current,
    )


if __name__ == "__main__":
    main()
