"""Shared logging setup and structured key/value helpers for Python jobs."""

from __future__ import annotations

import logging
import os
import sys

DEFAULT_LOG_LEVEL = "INFO"
_THIRD_PARTY_WARNING_LOGGERS: tuple[str, ...] = (
    "twilio",
    "urllib3",
    "googleapiclient",
)


def configure_logging() -> None:
    """Configure process-wide logging for CLI jobs."""
    level_name = os.getenv("LOG_LEVEL", DEFAULT_LOG_LEVEL).upper()
    level = getattr(logging, level_name, logging.INFO)
    logging.basicConfig(
        level=level,
        stream=sys.stdout,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    for logger_name in _THIRD_PARTY_WARNING_LOGGERS:
        logging.getLogger(logger_name).setLevel(logging.WARNING)


def log_event(
    logger: logging.Logger,
    *,
    prefix: str,
    event: str,
    level: int = logging.INFO,
    **fields: object,
) -> None:
    """Emit ``prefix: event=... key=value ...`` via stdlib logging."""
    parts = [f"event={event}"]
    parts.extend(f"{key}={value}" for key, value in fields.items())
    logger.log(level, "%s: %s", prefix, " ".join(parts))
