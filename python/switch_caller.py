"""High-level operations for driving the remote-switch hardware over Twilio.

This module owns switch-domain knowledge (DTMF signals, polarity table, the
master-change SMS protocol). It depends on :mod:`twilio_api` for the actual
REST calls but takes the client by injection so it stays unit-testable.
"""

from __future__ import annotations

import logging
import time
from typing import Callable

from log_config import log_event
from twilio.twiml.voice_response import VoiceResponse

from repo_config import load_config
from twilio_api import LastCallStatus, TwilioClient
from twilio_api import get_client as get_twilio_client

# Prototype devices have inverted polarity: sending the "enable" signal
# disables them, and vice versa.
INVERTED_PHONE_NUMBERS: frozenset[str] = frozenset(
    {
        "+528713293364",
        "+528713971819",
        "+528713971823",
        "+528713865040",
        "+528713971807",
        "+528713460690",
    }
)

INITIAL_PAUSE_SECONDS = 10
BETWEEN_DIGIT_PLAYS_PAUSE_SECONDS = 10
DIGIT_PLAY_COUNT = 6
OUTBOUND_CALL_TIME_LIMIT_SECONDS = 70
POST_CALL_SLEEP_SECONDS = 80
POST_MASTER_CHANGE_SLEEP_SECONDS = 60

DTMF_ENABLE_SIGNAL = "w5"
DTMF_DISABLE_SIGNAL = "w1"

MASTER_CHANGE_PIN = "123456"
_LOG_PREFIX = "switch"
_LOGGER = logging.getLogger(__name__)


def _log(event: str, **fields: object) -> None:
    """Single-line structured log for switch operations."""
    log_event(_LOGGER, prefix=_LOG_PREFIX, event=event, **fields)


def _resolve_dtmf_digits(phone_number: str, enabled: bool) -> str:
    """Pick the DTMF digits that put ``phone_number`` into the desired state."""
    is_inverted = phone_number in INVERTED_PHONE_NUMBERS
    want_enable = enabled if not is_inverted else not enabled
    return DTMF_ENABLE_SIGNAL if want_enable else DTMF_DISABLE_SIGNAL


def _build_outbound_twiml(phone_number: str, enabled: bool) -> VoiceResponse:
    response = VoiceResponse()
    digits = _resolve_dtmf_digits(phone_number, enabled)
    response.pause(length=INITIAL_PAUSE_SECONDS)
    for _ in range(DIGIT_PLAY_COUNT):
        response.play("", digits=digits)
        response.pause(length=BETWEEN_DIGIT_PLAYS_PAUSE_SECONDS)
    return response


class SwitchCaller:
    """Place outbound calls / SMS to the remote switches via Twilio.

    All collaborators (Twilio client, master phone number, sleep function) are
    injected so tests can construct one with stubs.
    """

    def __init__(
        self,
        twilio: TwilioClient,
        master_phone_number: str,
        *,
        sleep: Callable[[float], None] = time.sleep,
    ):
        self._twilio = twilio
        self._master_phone_number = master_phone_number
        self._sleep = sleep

    def call_switch(self, phone_number: str, enabled: bool) -> str:
        """Place a DTMF-driven outbound call to toggle the switch and wait for
        it to settle. Returns the Twilio call SID.
        """
        _log("call_start", phone=phone_number, enabled=enabled)
        response = _build_outbound_twiml(phone_number, enabled)
        sid = self._twilio.create_call(
            to=phone_number,
            twiml=str(response),
            time_limit_seconds=OUTBOUND_CALL_TIME_LIMIT_SECONDS,
        )
        _log(
            "call_queued",
            phone=phone_number,
            enabled=enabled,
            sid=sid,
            sleep_seconds=POST_CALL_SLEEP_SECONDS,
        )
        self._sleep(POST_CALL_SLEEP_SECONDS)
        return sid

    def call_switch_with_retries(
        self,
        phone_number: str,
        enabled: bool,
        *,
        max_retries: int,
    ) -> tuple[str, bool]:
        """Call the switch, retrying when the last call did not complete.

        Makes up to ``max_retries + 1`` attempts (one initial call plus
        ``max_retries`` retries). Returns ``(final_sid, succeeded)`` where
        ``succeeded`` is True when the last attempt's status is ``completed``.
        """
        last_sid = ""
        last_call: LastCallStatus | None = None
        for attempt in range(max_retries + 1):
            last_sid = self.call_switch(phone_number, enabled)
            last_call = self._twilio.get_last_call_status(phone_number)
            if last_call is not None and last_call.status == "completed":
                _log(
                    "call_completed",
                    phone=phone_number,
                    enabled=enabled,
                    sid=last_sid,
                    attempt=attempt + 1,
                )
                return last_sid, True
            if attempt < max_retries:
                _log(
                    "call_retry",
                    phone=phone_number,
                    enabled=enabled,
                    sid=last_sid,
                    attempt=attempt + 1,
                    last_status=last_call.status if last_call else None,
                )
        _log(
            "call_exhausted_retries",
            phone=phone_number,
            enabled=enabled,
            sid=last_sid,
            max_retries=max_retries,
            last_status=last_call.status if last_call else None,
        )
        return last_sid, False

    def change_master(self, phone_number: str) -> str:
        """Send the SMS that points the switch's master phone number to ours."""
        _log("master_change_start", phone=phone_number)
        body = f"*{MASTER_CHANGE_PIN}*#{self._master_phone_number}#"
        sid = self._twilio.send_message(to=phone_number, text=body)
        _log("master_change_sent", phone=phone_number, sid=sid)
        return sid


def get_switch_caller() -> SwitchCaller:
    """Default production wiring: real Twilio client + master phone from config."""
    return SwitchCaller(
        twilio=get_twilio_client(),
        master_phone_number=load_config()["twilio_master_phone_number"],
    )
