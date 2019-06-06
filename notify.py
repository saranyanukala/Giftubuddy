from datetime import datetime, timedelta
from flask import Flask
import time
from app import User,Userfriends,create_app
from flask_mail import Mail, Message
from sqlalchemy import extract, and_
import schedule

app = create_app()
app.app_context().push()
mail_settings = {
    "MAIL_SERVER": 'smtp.gmail.com',
    "MAIL_PORT": 465,
    "MAIL_USE_TLS": False,
    "MAIL_USE_SSL": True,
    "MAIL_USERNAME": 'saranya.nukala1@gmail.com',
    "MAIL_PASSWORD": '***'
}
app.config.update(mail_settings)
mail = Mail(app)

DAYS_IN_ADVANCE = 0
TODAY = datetime.now() + timedelta(days=DAYS_IN_ADVANCE)

def email():
	msg = Message(subject="Hello",
                      sender=app.config.get("MAIL_USERNAME"),
                      recipients=['saranya.nukala1@gmail.com'], 
                      body="This is a test email I sent with Gmail and Python!")
	x = mail.send(msg)

if __name__ == '__main__':
  schedule.every(2).minutes.do(job)
   # schedule.every().day.at('19:50').do(email)
  while True:
  	schedule.run_pending()
 ime.sleep(1)
