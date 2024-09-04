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


def get_trs(emails):
    gen_trs = []

    for email in emails:
        tr = f"""<tr>
        <td>{email["subj"]}</td>
            <td>{email["snippet"]}</td>
            <td><button>{email["to_delete"]}</button></td>
        </tr>"""
        gen_trs.append(tr)

    # join trs and get string
    return "\n".join(gen_trs)


def generate_actions_table(emails):
    generated_content = get_trs(emails)
    html = (
        """<!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Simple HTML Table</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    margin: 20px;
                    background-color: #f9f9f9;
                }
                table {
                    width: 100%;
                    border-collapse: collapse;
                    margin: 20px 0;
                    background-color: #ffffff;
                    border-radius: 8px;
                    overflow: hidden;
                    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                }
                th, td {
                    padding: 12px;
                    text-align: left;
                    border-bottom: 1px solid #ddd;
                }
                th {
                    background-color: #f4a261;
                    color: #fff;
                }
                tr:hover {
                    background-color: #f1f1f1;
                }
                button {
                    background-color: #2a9d8f;
                    color: white;
                    border: none;
                    padding: 8px 12px;
                    border-radius: 4px;
                    cursor: pointer;
                }
                button:hover {
                    background-color: #1f6f56;
                }
            </style>
        </head>
        <body>

        <h2>Here are your emails and the actions taken</h2>

        <table>
            <thead>
                <tr>
                    <th>Subject</th>
                    <th>Snippet</th>
                    <th>Action</th>
                </tr>
            </thead>
            <tbody>"""
        + generated_content
        + """
            </tbody>
        </table>

        </body>
        </html>
        """
    )

    return html
