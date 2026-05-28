import base64
import os
from pathlib import Path
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

class GmailIngestor:
    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

    def __init__(self, credentials_path='credentials.json', token_path='token.json', ingest_dir='__ingest'):
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.ingest_dir = Path(ingest_dir)
        self.service = None

    def authenticate(self):
        creds = None
        if os.path.exists(self.token_path):
            creds = Credentials.from_authorized_user_file(self.token_path, self.SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(self.credentials_path, self.SCOPES)
                creds = flow.run_local_server(port=0)
            with open(self.token_path, 'w') as token:
                token.write(creds.to_json())
        self.service = build('gmail', 'v1', credentials=creds)

    # Helper functions to extract email data
    def get_header_value(self, headers, header_name):
        for header in headers:
            if header.get("name", "").lower() == header_name.lower():
                return header.get("value", "")
        return ""

    # Helper function to decode base64 data, handling padding issues
    def decode_base64_bytes(self, data):
        if not data:
            return ""
        padding = len(data) % 4
        if padding:
            data += "=" * (4 - padding)  # Add necessary padding
        return base64.urlsafe_b64decode(data)
    
    def decode_base64_text(self, data):
        return self.decode_base64_bytes(data).decode("utf-8", errors="ignore")

    # Extract the email body, handling both plain text and multipart emails
    def extract_email_body(self, payload):
        body = ""
        if "parts" in payload:
            for part in payload["parts"]:
                mime_type = part.get("mimeType", "")
                if mime_type == "text/plain":
                    data = part.get("body", {}).get("data", "")
                    body += self.decode_base64_text(data)
                elif "parts" in part:
                    body += self.extract_email_body(part)  # Recursively extract from nested parts
        else:
            data = payload.get("body", {}).get("data", "")
            body += self.decode_base64_text(data)
        return body

    # Convert Gmail API message to our processed document format
    def parse_email_to_processed_object(self, message):
        headers = message["payload"].get("headers", [])
        subject = self.get_header_value(headers, "Subject")
        sender = self.get_header_value(headers, "From")
        date = self.get_header_value(headers, "Date")
        message_id = message.get("id", "")
        body = self.extract_email_body(message["payload"])
        return {
            "title": subject,
            "paragaphs": body,
            "header_footer": f"From: {sender}\nDate: {date}\nMessage-ID: {message_id}",
            "table_content": "",
            "author": sender,
            "time_creation": date,
            "modified_date": "",
            "file_computer_id": message_id,
            "doc_hash": ""
        }

    # Fetch email message IDs from the user's inbox
    def fetch_message_ids(self, max_results=10):
        results = self.service.users().messages().list(
            userId='me', 
            labelIds=['INBOX'],
            maxResults=max_results
        ).execute()
        return results.get('messages', [])
    
    # Fetch a single email message by ID, with specified format (default is 'full' for all metadata and body)
    def fetch_message(self, message_id, fmt='full'):
        return self.service.users().messages().get(
            userId='me', 
            id=message_id,
            format=fmt
        ).execute()
    
    # Save the raw email content to a file for reference, using the message ID as the filename
    def save_raw_email(self, message_id):
        raw_message = self.fetch_message(message_id, fmt='raw')
        raw_data = raw_message.get("raw", "")
        email_bytes = self.decode_base64_bytes(raw_data)
        
        self.ingest_dir.mkdir(parents=True, exist_ok=True)
        output_path = self.ingest_dir / f"{message_id}.eml"

        with open(output_path, "wb") as f:
            f.write(email_bytes)

        return output_path
    
    # Main function to run the ingestion process: authenticate, fetch messages, process them, and save raw emails
    def run(self, max_emails=10):
        self.authenticate()
        message_ids = self.fetch_message_ids(max_results=max_emails)
        processed_documents = []
        for msg in message_ids:
            message_id = msg["id"]
            email_message = self.fetch_message(message_id)
            processed_doc = self.parse_email_to_processed_object(email_message)
            processed_documents.append({
                "parsed_email": processed_doc,
                "saved_to": str(saved_path) 
                if (saved_path := self.save_raw_email(message_id)) else "Failed to save"
            })
            self.save_raw_email(message_id)  # Save raw email for reference
        return processed_documents