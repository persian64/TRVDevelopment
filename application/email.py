from flask_mail import Message
from app import trv, mail

def send_email(to, subject, template):
    msg = Message(
        subject=subject,
        recipients=[to],
        html=template,
        sender='no-reply@researchersvalley.org'
    )
    mail.send(msg)


