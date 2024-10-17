import re
import quopri
import base64
from bs4 import BeautifulSoup
import email

def subject_needs_decoding(subject):
    # Regular expression to detect MIME-encoded strings
    mime_encoded_pattern = r'=\?.+\?.\?.+\?='

    # Check if the subject matches the MIME-encoded pattern
    if re.search(mime_encoded_pattern, subject):
        return True
    else:
        return False

def decode_subject(encoded_subject):
    # Regular expression to match MIME encoded parts
    mime_regex = r'=\?([^?]+)\?([BQ])\?([^?]+)\?='

    def decode_part(match):
        charset, encoding, encoded_text = match.groups()

        if encoding.upper() == 'B':  # Base64 encoding
            decoded_bytes = base64.b64decode(encoded_text)
        elif encoding.upper() == 'Q':  # Quoted-Printable encoding
            # Replace underscores with spaces (MIME Quoted-Printable uses _ for space)
            encoded_text = encoded_text.replace('_', ' ')
            decoded_bytes = quopri.decodestring(encoded_text)
        else:
            raise ValueError(f"Unknown encoding type: {encoding}")

        return decoded_bytes.decode(charset, errors='replace')

    # Apply the regex to find and decode all encoded parts in the subject
    decoded_subject = re.sub(mime_regex, decode_part, encoded_subject)

    return decoded_subject

def get_email_subject(raw_email_base64):

    if not raw_email_base64:
        return None

    raw_email = base64.urlsafe_b64decode(raw_email_base64).decode("utf-8")
    msg = email.message_from_string(raw_email)

    subject = msg["Subject"] or None
    if subject and subject_needs_decoding(subject):
        subject = decode_subject(subject)

    return subject


def get_email_message_id(raw_email_base64):
    if not raw_email_base64:
        return None

    raw_email = base64.urlsafe_b64decode(raw_email_base64).decode("utf-8")
    msg = email.message_from_string(raw_email)

    message_id = msg["Message-ID"] or None
    return message_id


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
