"""Weekly job: email a report of the remote-switch fleet status."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timezone
import logging

from firebase_api import DatabaseDevice, get_devices
from gmail_api import GmailClient, GmailMessage
from log_config import configure_logging, log_event
from repo_config import load_config
from twilio_api import LastCallStatus, TwilioClient, get_client

REPORT_SUBJECT = "Reporte semanal switch remoto"

_DASH = "-"
_LOG_PREFIX = "report"
_LOGGER = logging.getLogger(__name__)


def _log(event: str, **fields: object) -> None:
    """Single-line, structured log for report generation and delivery."""
    log_event(_LOGGER, prefix=_LOG_PREFIX, event=event, **fields)


@dataclass(frozen=True)
class ReportRow:
    serial_number: str
    phone_number: str
    client_name: str
    client_number: str
    status: str
    days: str


def _days_since(dt: datetime | None) -> int | None:
    if dt is None:
        return None
    return (datetime.now(timezone.utc) - dt).days


def _format_days_since(days_since: int | None) -> str:
    if days_since is None:
        return _DASH
    if days_since == 1:
        return "Hace 1 día"
    return f"Hace {days_since} días"


def _row_to_html(row: ReportRow) -> str:
    return f"""
    <tr>
        <td>{row.serial_number}</td>
        <td>{row.phone_number}</td>
        <td>{row.client_name}</td>
        <td>{row.client_number}</td>
        <td>{row.status}</td>
        <td>{row.days}</td>
    </tr>
    """


def _build_rows_html(rows: list[ReportRow]) -> str:
    return "".join(_row_to_html(row) for row in rows)


def _build_row(
    twilio: TwilioClient, device: DatabaseDevice, last_status: LastCallStatus | None
) -> ReportRow:
    last_completed = (
        twilio.get_last_completed_call_date(device.phone_number)
        if device.phone_number
        else None
    )
    return ReportRow(
        serial_number=device.serial_number or _DASH,
        phone_number=device.phone_number or _DASH,
        client_name=device.client_name or _DASH,
        client_number=device.client_number or _DASH,
        status=last_status.status if last_status is not None else _DASH,
        days=_format_days_since(_days_since(last_completed)),
    )


def _fetch_status(
    twilio: TwilioClient, phone_number: str
) -> LastCallStatus | None:
    if not phone_number:
        return None
    return twilio.get_last_call_status(phone_number)


def build_report(devices: list[DatabaseDevice]) -> str:
    twilio = get_client()
    inactive_rows: list[ReportRow] = []
    active_rows: list[ReportRow] = []
    total_active_completed_devices = 0

    for device in devices:
        last_status = _fetch_status(twilio, device.phone_number)
        if device.is_active is False:
            inactive_rows.append(_build_row(twilio, device, last_status))
            continue

        status_str = last_status.status if last_status is not None else "unknown"
        if status_str != "completed":
            active_rows.append(_build_row(twilio, device, last_status))
        else:
            total_active_completed_devices += 1

    # NOTE: sort key is a Spanish string ("Hace N días"). Preserved for now
    # so the report ordering stays consistent with the previous version.
    inactive_rows.sort(key=lambda row: row.days, reverse=True)
    active_rows.sort(key=lambda row: row.days, reverse=True)

    _log(
        "report_compiled",
        total_devices=len(devices),
        total_active_completed_devices=total_active_completed_devices,
        total_active_incomplete_devices=len(active_rows),
        total_inactive_devices=len(inactive_rows),
    )

    return _render_report_html(
        report_date=date.today(),
        total_devices=len(devices),
        total_active_completed_devices=total_active_completed_devices,
        total_active_incomplete_devices=len(active_rows),
        total_inactive_devices=len(inactive_rows),
        active_rows_html=_build_rows_html(active_rows),
        inactive_rows_html=_build_rows_html(inactive_rows),
    )


def _render_report_html(
    *,
    report_date: date,
    total_devices: int,
    total_active_completed_devices: int,
    total_active_incomplete_devices: int,
    total_inactive_devices: int,
    active_rows_html: str,
    inactive_rows_html: str,
) -> str:
    return f"""
<html>
<head>
<style>
h1 {{font-family: Helvetica, Arial, sans-serif; font-weight: normal}}
h2 {{font-family: Helvetica, Arial, sans-serif; font-weight: normal}}
h3 {{font-family: Helvetica, Arial, sans-serif; font-weight: normal}}
h4 {{font-family: Helvetica, Arial, sans-serif; font-weight: normal}}

#actives {{font-family: Helvetica, Arial, sans-serif; border-collapse: collapse;}}
#actives td, #actives th {{border: 1px solid #ddd; padding: 8px;}}
#actives tr:nth-child(even){{background-color: #f2f2f2;}}
#actives tr:hover {{background-color: #ddd;}}
#actives th {{
  padding-top: 12px;
  padding-bottom: 12px;
  text-align: left;
  background-color: #0270c9;
  color: white;
}}

#inactives {{font-family: Helvetica, Arial, sans-serif; border-collapse: collapse;}}
#inactives td, #inactives th {{border: 1px solid #ddd; padding: 8px;}}
#inactives tr:nth-child(even){{background-color: #f2f2f2;}}
#inactives tr:hover {{background-color: #ddd;}}
#inactives th {{
  padding-top: 12px;
  padding-bottom: 12px;
  text-align: left;
  background-color: #0270c9;
  color: white;
}}
</style>
</head>
<body>
<h1>Reporte semanal</h1>
<h3>Fecha: {report_date}</h3>
<h4>Total de dispositivos: {total_devices}</h4>
<h4>Total de dispositivos activos con llamada completada: {total_active_completed_devices}</h4>
<h4>Total de dispositivos activos con llamada no completada: {total_active_incomplete_devices}</h4>
<h4>Total de dispositivos inactivos: {total_inactive_devices}</h4>

<h2>Tabla de activos</h2>
<table id="actives">
  <tr>
    <th>No. de serie</th>
    <th>No. de celular</th>
    <th>Cliente</th>
    <th>No. de cliente</th>
    <th>Estatus</th>
    <th>Último enlace</th>
  </tr>
  {active_rows_html}
</table>

<h2>Tabla de inactivos</h2>
<table id="inactives">
  <tr>
    <th>No. de serie</th>
    <th>No. de celular</th>
    <th>Cliente</th>
    <th>No. de cliente</th>
    <th>Estatus</th>
    <th>Último enlace</th>
  </tr>
  {inactive_rows_html}
</table>
</body>
</html>
"""


def send_email(body: str) -> None:
    cfg = load_config()
    message = GmailMessage(
        to=cfg["weekly_report_to_email"],
        from_email=cfg["from_email"],
        cc=cfg["weekly_report_cc_emails"],
        subject=REPORT_SUBJECT,
        html_body=body,
    )
    result = GmailClient().send_html_email(message)
    _log("email_sent", message_id=result.message_id, to=cfg["weekly_report_to_email"])


def main() -> None:
    configure_logging()
    devices = get_devices()
    send_email(build_report(devices))


if __name__ == "__main__":
    main()
