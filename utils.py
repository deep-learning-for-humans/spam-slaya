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


def test_ai():
    # TODO: add implementation
    client = OpenAI()

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Tell a joke to my 3sb friends."},
        ],
    )

    print(completion.choices[0].message)
    return completion.choices[0].message
