import instructor
from openai import OpenAI
from pydantic import BaseModel

from ..config import Config

PROMPT = """You are an advanced email classification model. Your task is to analyze email content and determine whether to DELETE or KEEP the email based on its content, source, and purpose.

**Criteria for DELETE:**  
- Emails related to advertisements, promotions, or marketing (e.g., offers, discounts, sales campaigns).  
- Generic newsletters, spam, or unsolicited content.
- Delete OTP emails if and only if they are older than 1 week using the "Days elapsed since receiving email" field 

**Criteria for KEEP:**  
- Transactional emails (e.g., receipts, invoices, account alerts, subscription confirmations).  
- Personal emails (from friends, family, or known contacts which are not from social media).  
- Emails from trusted or important sources (e.g., financial institutions, government organizations).  
- Any emails related to professional matters, appointments, or important updates.

**Instructions:**  
- If the email content fits any of the DELETE or KEEP criteria, respond only with a JSON object containing:
  - **action**: "KEEP" or "DELETE" based on your decision.
  - **reason**: A brief reason (e.g., "OTP", "Txn" for transactions, "Ad" for advertisements, "Spam" for spam, "Personal" for personal emails).
  - **confidence**: One of the 3 values HIGH, MEDIUM, or LOW, representing the confidence of the classification.

**Examples:**  
```json
{'action': 'KEEP', 'reason': 'Txn', 'confidence': 'MEDIUM'}
{'action': 'DELETE', 'reason': 'Ad', 'confidence': 'HIGH'}
{'action': 'DELETE', 'reason': 'Spam', 'confidence': 'LOW'}
```

**Important Notes:**  
- The list of DELETE and KEEP categories provided is not exhaustive. Use your judgment to recognize important emails not explicitly mentioned and classify them accordingly.  
- Always respond only in JSON format without additional text or explanations.
"""

class MailAction(BaseModel):
    action: str
    reason: str
    confidence: str


def infer_email_type(subject, body, time_diff_in_days):
    client = instructor.from_openai(
        OpenAI(
            base_url=f"{Config.OLLAMA_URL}/v1",
            api_key=Config.OLLAMA_API_KEY
            ),
        mode=instructor.Mode.JSON,
    )

    first_500_words = " ".join(body.split()[:500])

    message_to_infer = f"Days elapsed since receiving email: {time_diff_in_days}\nSubject: {subject}\nBody:{first_500_words}"
    print(f"{time_diff_in_days}: {subject}")

    response = client.chat.completions.create(
        model=Config.OLLAMA_MODEL,
        messages=[
            {"role": "system", "content": PROMPT},
            {"role": "user", "content": message_to_infer},
        ],
        temperature=0.00001,
        top_p=1.0,
        response_model=MailAction,
    )

    return response
