import base64
from pathlib import Path
import re
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request

from .gmail_api_interface import Interface_GmailIngestor


class GmailIngestor(Interface_GmailIngestor):
    SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

    def __init__(
        self,
        processed_document_cls,
        credentials_path: str,
        ingest_dir: str,
        redirect_uri: str,
    ):
        self.Processed_Document_Obj = processed_document_cls
        self.credentials_path = credentials_path
        self.ingest_dir = Path(ingest_dir)
        self.redirect_uri = redirect_uri
        self.creds = None
        self.service = None

    def _build_flow(self, state: str | None = None) -> Flow:
        flow = Flow.from_client_secrets_file(
            self.credentials_path,
            scopes=self.SCOPES,
            state=state,
        )
        flow.redirect_uri = self.redirect_uri
        return flow

    def _build_flow(self, state: str | None = None, code_verifier: str | None = None) -> Flow:
        flow = Flow.from_client_secrets_file(
            self.credentials_path,
            scopes=self.SCOPES,
            state=state,
        )
        flow.redirect_uri = self.redirect_uri

        if code_verifier:
            flow.code_verifier = code_verifier

        return flow


    def build_auth_url(self, state: str, code_verifier: str) -> tuple[str, str]:
        flow = self._build_flow(state=state, code_verifier=code_verifier)

        auth_url, returned_state = flow.authorization_url(
            access_type="offline",
            include_granted_scopes="true",
            prompt="consent",
        )
        return auth_url, returned_state


    def exchange_code_for_tokens(self, code: str, state: str, code_verifier: str):
        flow = self._build_flow(state=state, code_verifier=code_verifier)
        flow.fetch_token(code=code)

        creds = flow.credentials
        return {
            "token": creds.token,
            "refresh_token": creds.refresh_token,
            "token_uri": creds.token_uri,
            "client_id": creds.client_id,
            "client_secret": creds.client_secret,
            "scopes": creds.scopes,
        }

    def set_credentials_from_token_info(self, token_info: dict) -> None:
        creds = Credentials(
            token=token_info["token"],
            refresh_token=token_info.get("refresh_token"),
            token_uri=token_info.get("token_uri", "https://oauth2.googleapis.com/token"),
            client_id=token_info["client_id"],
            client_secret=token_info["client_secret"],
            scopes=token_info.get("scopes", self.SCOPES),
        )

        if creds.expired and creds.refresh_token:
            creds.refresh(Request())

        self.creds = creds
        self.service = build("gmail", "v1", credentials=creds)

    def get_header_value(self, headers, header_name):
        for header in headers:
            if header.get("name", "").lower() == header_name.lower():
                return header.get("value", "")
        return ""

    def decode_base64_bytes(self, data):
        if not data:
            return b""
        padding = len(data) % 4
        if padding:
            data += "=" * (4 - padding)
        return base64.urlsafe_b64decode(data)

    def decode_base64_text(self, data):
        return self.decode_base64_bytes(data).decode("utf-8", errors="ignore")

    def extract_email_body(self, payload):
        plain_parts = []
        html_parts = []

        def walk(part):
            mime_type = part.get("mimeType", "")
            body_data = part.get("body", {}).get("data", "")

            if mime_type == "text/plain" and body_data:
                plain_parts.append(self.decode_base64_text(body_data))
            elif mime_type == "text/html" and body_data:
                html_parts.append(self.decode_base64_text(body_data))

            for child in part.get("parts", []) or []:
                walk(child)

        walk(payload)

        if plain_parts:
            return "\n".join(p.strip() for p in plain_parts if p and p.strip())

        if html_parts:
            html_text = "\n".join(p for p in html_parts if p)
            html_text = html_text.replace("<br>", "\n").replace("<br/>", "\n").replace("<br />", "\n")
            html_text = html_text.replace("</p>", "\n").replace("</div>", "\n")
            html_text = re.sub(r"<[^>]+>", " ", html_text)
            html_text = re.sub(r"\s+", " ", html_text).strip()
            return html_text

        data = payload.get("body", {}).get("data", "")
        return self.decode_base64_text(data).strip()

    def parse_email_to_processed_object(self, message):
        headers = message.get("payload", {}).get("headers", [])
        subject = self.get_header_value(headers, "Subject") or "Untitled email"
        sender = self.get_header_value(headers, "From") or ""
        date = self.get_header_value(headers, "Date") or ""
        message_id = message.get("id", "")
        body = self.extract_email_body(message.get("payload", {})) or ""

        return self.Processed_Document_Obj(
            title=subject,
            paragaphs=body,
            header_footer=f"From: {sender}\nDate: {date}\nMessage-ID: {message_id}",
            table_content="",
            author=sender,
            time_creation=date,
            modified_date=date,
            file_computer_id=message_id,
        )

    def fetch_message_ids(self, max_results=10):
        results = (
            self.service.users()
            .messages()
            .list(userId="me", labelIds=["INBOX"], maxResults=max_results)
            .execute()
        )
        return results.get("messages", [])

    def fetch_message(self, message_id, fmt="full"):
        return (
            self.service.users()
            .messages()
            .get(userId="me", id=message_id, format=fmt)
            .execute()
        )

    def save_raw_email(self, message_id):
        raw_message = self.fetch_message(message_id, fmt="raw")
        raw_data = raw_message.get("raw", "")
        email_bytes = self.decode_base64_bytes(raw_data)

        self.ingest_dir.mkdir(parents=True, exist_ok=True)
        output_path = self.ingest_dir / f"{message_id}.eml"

        with open(output_path, "wb") as f:
            f.write(email_bytes)

        return output_path

    def ingest_gmail(self, max_emails=10):
        if not self.service:
            raise RuntimeError("Gmail service not initialized")

        processed_documents = []

        for msg in self.fetch_message_ids(max_results=max_emails):
            message_id = msg["id"]
            email_message = self.fetch_message(message_id, fmt="full")

            processed_doc = self.parse_email_to_processed_object(email_message)
            save_path = self.save_raw_email(message_id)

            subject = processed_doc.title or "Untitled email"
            sender = processed_doc.author or ""
            date = processed_doc.time_creation or ""
            body = processed_doc.paragaphs or ""

            processed_documents.append(
                {
                    "message_id": message_id,
                    "subject": subject,
                    "sender": sender,
                    "date": date,
                    "body": body,
                    "saved_to": str(save_path),
                    "processed_doc": processed_doc,
                }
            )

        return processed_documents