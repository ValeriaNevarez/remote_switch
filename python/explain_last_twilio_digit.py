"""Explain whether the latest Twilio call to a phone sent DTMF 5 or 1.

Twilio stores the API request that created a call in the Call Events
subresource. Those events are usually available about 15 minutes after the call
ends.

Run from ``python`` after loading env vars::

    python explain_last_twilio_digit.py +528711234567
"""

from __future__ import annotations

import argparse
from typing import Any
import xml.etree.ElementTree as ET

from twilio_api import TwilioCallRecord, get_client


def _normalize_phone_number(raw: str) -> str:
    phone = raw.strip()
    if phone.startswith("+"):
        return phone

    digits = "".join(ch for ch in phone if ch.isdigit())
    if len(digits) == 10:
        return f"+52{digits}"
    if len(digits) == 12 and digits.startswith("52"):
        return f"+{digits}"
    return phone


def _event_mapping(value: object) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    if value is None:
        return {}
    return {
        key: getattr(value, key)
        for key in dir(value)
        if not key.startswith("_") and not callable(getattr(value, key))
    }


def _event_request(event: object) -> dict[str, Any]:
    return _event_mapping(getattr(event, "request", None))


def _request_parameters(event: object) -> dict[str, Any]:
    request = _event_request(event)
    params = request.get("parameters") or request.get("Parameters")
    return _event_mapping(params)


def _find_twiml(events: list[object]) -> str | None:
    for event in events:
        params = _request_parameters(event)
        for key, value in params.items():
            if key.lower() == "twiml" and value:
                return str(value)
    return None


def _extract_play_digits(twiml: str) -> list[str]:
    try:
        root = ET.fromstring(twiml)
    except ET.ParseError:
        return []

    digits: list[str] = []
    for element in root.iter():
        if element.tag.split("}")[-1].lower() != "play":
            continue
        value = element.attrib.get("digits")
        if value:
            digits.append(value)
    return digits


def _pressed_digit(play_digits: list[str]) -> str | None:
    for value in play_digits:
        if value.endswith("5"):
            return "5"
        if value.endswith("1"):
            return "1"
    return None


def _print_call(call: TwilioCallRecord) -> None:
    print(f"Call SID: {call.sid}")
    print(f"To: {call.to}")
    print(f"From: {call.from_}")
    print(f"Status: {call.status}")
    print(f"Date: {call.date}")
    print(f"Duration seconds: {call.duration_seconds}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Find whether the latest Twilio call to a phone sent DTMF 5 or 1."
    )
    parser.add_argument(
        "phone_number",
        help="Phone number to query. 10 Mexican digits are normalized to +52.",
    )
    args = parser.parse_args()

    phone_number = _normalize_phone_number(args.phone_number)
    twilio = get_client()
    call = twilio.get_last_call_record(phone_number)
    if call is None:
        print(f"No Twilio calls found to {phone_number}.")
        return

    _print_call(call)
    events = twilio.get_call_events(call.sid)
    if not events:
        print(
            "No call events found yet. Twilio says Call Events are usually "
            "available about 15 minutes after a call ends."
        )
        return

    twiml = _find_twiml(events)
    if not twiml:
        print("No inline TwiML parameter found in the call events.")
        return

    play_digits = _extract_play_digits(twiml)
    digit = _pressed_digit(play_digits)
    print(f"TwiML: {twiml}")
    print(f"Play digits: {', '.join(play_digits) if play_digits else '(none)'}")
    print(f"Pressed digit: {digit if digit else 'unknown'}")


if __name__ == "__main__":
    main()
