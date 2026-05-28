import base64

# Helper functions to extract email data
def get_header_value(headers, header_name):
    for header in headers:
        if header.get("name", "").lower() == header_name.lower():
            return header.get("value", "")
    return ""

def decode_base64_data(data):
    if not data:
        return ""
    padding = len(data) % 4
    if padding:
        data += "=" * (4 - padding)  # Add necessary padding
    return base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")

# Extract the email body, handling both plain text and multipart emails
def extract_email_body(payload):
    body = ""
    if "parts" in payload:
        for part in payload["parts"]:
            mime_type = part.get("mimeType", "")
            if mime_type == "text/plain":
                data = part.get("body", {}).get("data", "")
                body += decode_base64_data(data)
            elif "parts" in part:
                body += extract_email_body(part)  # Recursively extract from nested parts
    else:
        data = payload.get("body", {}).get("data", "")
        body += decode_base64_data(data)
    return body

# Convert Gmail API message to our processed document format
def parse_email_to_processed_object(message):
    headers = message["payload"].get("headers", [])
    subject = get_header_value(headers, "Subject")
    sender = get_header_value(headers, "From")
    date = get_header_value(headers, "Date")
    message_id = message.get("id", "")
    body = extract_email_body(message["payload"])
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