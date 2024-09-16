import base64
from bs4 import BeautifulSoup
import email


def get_email_subject(raw_email_base64):

    if not raw_email_base64:
        return None

    raw_email = base64.urlsafe_b64decode(raw_email_base64).decode("utf-8")
    msg = email.message_from_string(raw_email)

    return msg["Subject"] or None


def get_email_body(raw_email_base64):
    if not raw_email_base64:
        return None

    raw_email = base64.urlsafe_b64decode(raw_email_base64)
    msg = email.message_from_bytes(raw_email)

    def decode_payload(payload, charset=None):
        if charset:
            try:
                return payload.decode(charset)
            except UnicodeDecodeError:
                pass

        # Try common encodings
        for encoding in ['utf-8', 'latin-1', 'ascii', 'windows-1252']:
            try:
                return payload.decode(encoding)
            except UnicodeDecodeError:
                continue

        # If all else fails, decode with errors ignored
        return payload.decode('utf-8', errors='ignore')

    body = None

    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            if content_type == "text/plain":
                payload = part.get_payload(decode=True)
                charset = part.get_content_charset()
                body = decode_payload(payload, charset)
                break
            elif content_type == "text/html":
                payload = part.get_payload(decode=True)
                charset = part.get_content_charset()
                html_content = decode_payload(payload, charset)
                body = extract_text_from_html(html_content)
                break
    else:
        content_type = msg.get_content_type()
        payload = msg.get_payload(decode=True)
        charset = msg.get_content_charset()
        if content_type == "text/plain":
            body = decode_payload(payload, charset)
        elif content_type == "text/html":
            html_content = decode_payload(payload, charset)
            body = extract_text_from_html(html_content)

    return body or None


def extract_text_from_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    return soup.get_text(separator='\n', strip=True)
