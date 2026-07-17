"""
Gmail API Test Script
======================
Tests Gmail API connection and fetches emails for demo.

Usage:
    cd C:/Users/Philip/Documents/GitHub/4260_presentation
    C:/Users/Philip/AppData/Local/Programs/Python/Python314/python.exe test_gmail.py

Prerequisites:
    pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
"""

import os
import json
from pathlib import Path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import base64

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
CREDENTIALS_PATH = "Modules/gmail_api/credentials.json"
TOKEN_PATH = "Modules/gmail_api/token.json"


def get_gmail_service():
    """Authenticate and return Gmail service."""
    creds = None

    # Load existing token if available
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)

    # If no valid credentials, do OAuth flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)

        # Save token for next time
        with open(TOKEN_PATH, "w") as token:
            token.write(creds.to_json())
        print(f"[auth] Token saved to {TOKEN_PATH}")

    service = build("gmail", "v1", credentials=creds)
    print("[auth] Gmail API connected successfully!")
    return service


def get_email_body(payload):
    """Extract email body text."""
    body = ""
    if "parts" in payload:
        for part in payload["parts"]:
            if part.get("mimeType") == "text/plain":
                data = part.get("body", {}).get("data", "")
                if data:
                    body += base64.urlsafe_b64decode(data + "==").decode("utf-8", errors="ignore")
    else:
        data = payload.get("body", {}).get("data", "")
        if data:
            body += base64.urlsafe_b64decode(data + "==").decode("utf-8", errors="ignore")
    return body


def fetch_emails(service, max_results=5):
    """Fetch latest emails from inbox."""
    print(f"\n[fetch] Fetching last {max_results} emails from inbox...")

    results = service.users().messages().list(
        userId="me",
        labelIds=["INBOX"],
        maxResults=max_results
    ).execute()

    messages = results.get("messages", [])
    print(f"[fetch] Found {len(messages)} messages.")

    emails = []
    for msg in messages:
        full_msg = service.users().messages().get(
            userId="me",
            id=msg["id"],
            format="full"
        ).execute()

        headers = full_msg.get("payload", {}).get("headers", [])
        subject = next((h["value"] for h in headers if h["name"] == "Subject"), "(no subject)")
        sender  = next((h["value"] for h in headers if h["name"] == "From"), "(unknown)")
        date    = next((h["value"] for h in headers if h["name"] == "Date"), "(unknown)")
        body    = get_email_body(full_msg.get("payload", {}))

        email = {
            "id": msg["id"],
            "subject": subject,
            "from": sender,
            "date": date,
            "body_preview": body[:200] + "..." if len(body) > 200 else body,
        }
        emails.append(email)
        print(f"\n  📧 {subject}")
        print(f"     From: {sender}")
        print(f"     Date: {date}")
        print(f"     Preview: {body[:100]}...")

    return emails


if __name__ == "__main__":
    print("=" * 60)
    print("  Gmail API Demo Test")
    print("=" * 60)

    # Check credentials file
    if not os.path.exists(CREDENTIALS_PATH):
        print(f"[error] credentials.json not found at {CREDENTIALS_PATH}")
        exit(1)

    # Connect to Gmail
    service = get_gmail_service()

    # Fetch emails
    emails = fetch_emails(service, max_results=1)

    print(f"\n[done] Successfully fetched {len(emails)} emails!")
    print("Gmail API is working correctly for demo.")
