import requests

domain = 'mg.noreplywp.com'
API_key = 'ab78b2973ee530ac2782f55e027a20f4-c5ea400f-893fc5ef'
recipient = 'mikke.molchan@gmail.com'



def send_email(recipient, subject, text):
    return requests.post(
        f"https://api.mailgun.net/v3/{domain}/messages",
        auth=("api", API_key),
        data={
            "from": f"Your App <mailgun@{domain}>",
            "to": recipient,
            "subject": subject,
            "text": text
        }
    )
