import base64
from bs4 import BeautifulSoup
import email
import instructor
from openai import OpenAI
from pydantic import BaseModel

INS = """you are an expert email analyzer. you check the content of the email and decide to delete or keep them.

* you decide to DELETE the email if they are advertisement regarding mutual funds , SIP advertizement, or stock markets general information, property Ads / posting.
* you decide to KEEP the email if they are shopping order, SIP trigger, SIP transaction details or Mutual Fund order details.

This is not the complete list of categories. You should understand other important emails and decide to keep it.

respond only by choosing DELETE / KEEP as a json
add a confidence score of your decision in the score field. score can be between 0.1 to 0.99, higher the value means higher the confidence.

Below are some example responses
{'action':'KEEP', 'reason':'Txn', 'score':0.7}
{'action':'DELETE', 'reason': 'Ad', 'score':0.95}
{'action':'DELETE', 'reason': 'Spam', 'score': 0.6}

you should err on the safer side
remember to respond only using json and nothing more."""


class MailAction(BaseModel):
    action: str
    reason: str
    score: float


def infer_email_type(user_msg):
    client = instructor.from_openai(
        OpenAI(),
        mode=instructor.Mode.JSON,
    )

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": INS},
            {"role": "user", "content": user_msg[:700]},
        ],
        temperature=0.00001,
        response_model=MailAction,
    )

    return response


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
