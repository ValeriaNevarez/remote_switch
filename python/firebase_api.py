"""Read and write device records in the Firebase Realtime Database."""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import Any

import firebase_admin
from firebase_admin import db

from env import load_json_from_base64_env, load_string_from_env

DEVICES_PATH = "/devices"


@dataclass(frozen=True)
class DatabaseDevice:
    serial_number: str
    phone_number: str
    enabled: bool
    is_active: bool
    client_name: str
    client_number: str
    is_manual_override: bool
    is_payment_current: bool
    key: str


class FirebaseClient:
    def __init__(self, database_url: str, service_account_info: dict[str, Any]):
        app = self._get_or_create_app(database_url, service_account_info)
        self._devices_ref = db.reference(DEVICES_PATH, app=app)

    @staticmethod
    def _get_or_create_app(
        database_url: str, service_account_info: dict[str, Any]
    ) -> firebase_admin.App:
        try:
            return firebase_admin.get_app()
        except ValueError:
            cred = firebase_admin.credentials.Certificate(service_account_info)
            return firebase_admin.initialize_app(cred, {"databaseURL": database_url})

    def _get_devices_raw(self) -> list[tuple[str, dict[str, Any]]]:
        """Return ``(key, item)`` tuples for every device, preserving DB keys."""
        payload = self._devices_ref.get()
        return self._payload_to_keyed_items(payload)

    @staticmethod
    def _payload_to_keyed_items(payload: Any) -> list[tuple[str, dict[str, Any]]]:
        """Normalize Firebase ``/devices`` payload into ``(key, item)`` tuples."""
        if isinstance(payload, dict):
            return [(str(k), v) for k, v in payload.items() if isinstance(v, dict)]
        if isinstance(payload, list):
            return [(str(i), v) for i, v in enumerate(payload) if isinstance(v, dict)]
        return []

    @staticmethod
    def _parse_device(item: dict[str, Any], *, key: str) -> DatabaseDevice:
        try:
            return DatabaseDevice(
                serial_number=item["serial_number"],
                phone_number=item["phone_number"],
                enabled=item["enabled"],
                is_active=item["is_active"],
                client_name=item["client_name"],
                client_number=item["client_number"],
                is_manual_override=item["is_manual_override"],
                is_payment_current=item["is_payment_current"],
                key=key,
            )
        except KeyError as e:
            raise RuntimeError(
                f"DatabaseDevice at {DEVICES_PATH}/{key} is missing required field {e}"
            ) from e

    def get_devices(self) -> list[DatabaseDevice]:
        return [self._parse_device(item, key=key) for key, item in self._get_devices_raw()]

    def update_device(self, key: str, fields: dict[str, Any]) -> None:
        """Patch the device at ``/devices/{key}`` with the given fields."""
        self._devices_ref.child(key).update(fields)


@lru_cache(maxsize=1)
def get_client() -> FirebaseClient:
    """Return the process-wide FirebaseClient (constructed lazily from env vars)."""
    return FirebaseClient(
        database_url=load_string_from_env("FIREBASE_DATABASE_URL"),
        service_account_info=load_json_from_base64_env("FIREBASE_SERVICE_ACCOUNT_B64"),
    )


def get_devices() -> list[DatabaseDevice]:
    return get_client().get_devices()


def update_device_payment_current(key: str, is_payment_current: bool) -> None:
    """Persist the latest ``is_payment_current`` value for one device."""
    get_client().update_device(key, {"is_payment_current": is_payment_current})


def update_device_enabled(key: str, enabled: bool) -> None:
    """Persist the latest ``enabled`` value for one device."""
    get_client().update_device(key, {"enabled": enabled})
