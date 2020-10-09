from flask_mail import Message
from app import trv, mail

def send_email(to, subject, template):
    msg = Message(
        subject=subject,
        recipients=[to],
        html=template,
        sender='The Researchers Valley'
    )
    mail.send(msg)


