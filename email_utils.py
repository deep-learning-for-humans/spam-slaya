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

    raw_email = base64.urlsafe_b64decode(raw_email_base64).decode("utf-8")
    msg = email.message_from_string(raw_email)

    body = None

    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            if content_type == "text/plain":
                body = part.get_payload(decode=True).decode()
                break
            elif content_type == "text/html":
                html_content = part.get_payload(decode=True).decode()
                body = extract_text_from_html(html_content)
                break
    else:
        content_type = msg.get_content_type()
        if content_type == "text/plain":
            body = msg.get_payload(decode=True).decode()
        elif content_type == "text/html":
            html_content = msg.get_payload(decode=True).decode()
            body = extract_text_from_html(html_content)

    return body or None


def extract_text_from_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    return soup.get_text(separator='\n', strip=True)
