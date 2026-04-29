"""Send HTML email through the Gmail REST API using an OAuth user token."""

from __future__ import annotations

import base64
import os
from dataclasses import dataclass
from email.message import EmailMessage
from typing import Any

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from env import load_json_from_base64_env

GMAIL_SCOPES = ["https://www.googleapis.com/auth/gmail.send"]
_TOKEN_FILE_NAME = "token.json"


@dataclass(frozen=True)
class GmailMessage:
    to: str
    from_email: str
    subject: str
    html_body: str
    cc: str | None = None


@dataclass(frozen=True)
class GmailSendResult:
    message_id: str


class GmailClient:
    def __init__(self, scopes: list[str] | None = None):
        self._scopes = scopes or GMAIL_SCOPES

    def _load_credentials(self) -> Credentials:
        # Both env vars are validated up-front: in CI, the OAuth client config
        # is unused (the token is always refreshable) but we want a fast,
        # consistent failure if either secret is missing.
        client_cfg = load_json_from_base64_env("GMAIL_OAUTH_CLIENT_B64")
        token_info = load_json_from_base64_env("GMAIL_TOKEN_B64")
        creds = Credentials.from_authorized_user_info(token_info, self._scopes)

        if creds and creds.valid:
            return creds
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            return creds
        return self._run_interactive_flow(client_cfg)

    def _run_interactive_flow(self, client_cfg: dict[str, Any]) -> Credentials:
        flow = InstalledAppFlow.from_client_config(client_cfg, self._scopes)
        creds = flow.run_local_server(port=0)
        self._persist_token(creds)
        return creds

    @staticmethod
    def _persist_token(creds: Credentials) -> None:
        token_path = os.path.join(os.path.dirname(__file__), _TOKEN_FILE_NAME)
        with open(token_path, "w", encoding="utf-8") as f:
            f.write(creds.to_json())

    @staticmethod
    def _to_email_message(message: GmailMessage) -> EmailMessage:
        email = EmailMessage()
        email["To"] = message.to
        email["From"] = message.from_email
        email["Subject"] = message.subject
        if message.cc:
            email["Cc"] = message.cc
        email.set_content(message.html_body, subtype="html")
        return email

    def send_html_email(self, message: GmailMessage) -> GmailSendResult:
        creds = self._load_credentials()
        email = self._to_email_message(message)
        encoded = base64.urlsafe_b64encode(email.as_bytes()).decode()

        try:
            service = build("gmail", "v1", credentials=creds)
            response = (
                service.users()
                .messages()
                .send(userId="me", body={"raw": encoded})
                .execute()
            )
        except HttpError as error:
            raise RuntimeError(
                f"An error occurred while sending Gmail message: {error}"
            ) from error

        message_id = str(response.get("id", ""))
        if not message_id:
            raise RuntimeError("Gmail API returned an empty message id.")
        return GmailSendResult(message_id=message_id)
