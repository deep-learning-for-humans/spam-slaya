import instructor
from openai import OpenAI
from pydantic import BaseModel

PROMPT = """You are an advanced email classification model. Your task is to analyze email content and determine whether to DELETE or KEEP the email based on its content, source, and purpose.

**Criteria for DELETE:**  
- Emails related to advertisements, promotions, or marketing (e.g., offers, discounts, sales campaigns).  
- Generic newsletters, spam, or unsolicited content.

**Criteria for KEEP:**  
- Transactional emails (e.g., receipts, invoices, account alerts, subscription confirmations).  
- Personal emails (from friends, family, or known contacts).  
- Emails from trusted or important sources (e.g., financial institutions, government organizations).  
- Any emails related to professional matters, appointments, or important updates.

**Instructions:**  
- If the email content fits any of the DELETE or KEEP criteria, respond only with a JSON object containing:
  - **action**: "KEEP" or "DELETE" based on your decision.
  - **reason**: A brief reason (e.g., "Txn" for transactions, "Ad" for advertisements, "Spam" for spam, "Personal" for personal emails).
  - **score**: A confidence score between 1 to 100, where higher values indicate greater confidence in your decision.

**Examples:**  
```json
{'action': 'KEEP', 'reason': 'Txn', 'score': 80}
{'action': 'DELETE', 'reason': 'Ad', 'score': 90}
{'action': 'DELETE', 'reason': 'Spam', 'score': 60}
```

**Important Notes:**  
- The list of DELETE and KEEP categories provided is not exhaustive. Use your judgment to recognize important emails not explicitly mentioned and classify them accordingly.  
- Always respond only in JSON format without additional text or explanations.
"""

class MailAction(BaseModel):
    action: str
    reason: str
    score: float


def infer_email_type(api_key, user_msg):
    client = instructor.from_openai(
        OpenAI(
            base_url="http://localhost:11434/v1",
            api_key=api_key
            ),
        mode=instructor.Mode.JSON,
    )

    response = client.chat.completions.create(
        model="qwen2.5:3b",
        messages=[
            {"role": "system", "content": PROMPT},
            {"role": "user", "content": user_msg[:700]},
        ],
        temperature=0.00001,
        response_model=MailAction,
    )

    return response
