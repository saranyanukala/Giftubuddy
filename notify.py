from datetime import datetime, timedelta
from flask import Flask
import time
from datetime import date,datetime
from app import db,User,Userfriends,create_app
from flask_mail import Mail, Message
from flask_sqlalchemy import SQLAlchemy
import schedule

app = create_app()
app.app_context().push()
mail_settings = {
    "MAIL_SERVER": 'smtp.gmail.com',
    "MAIL_PORT": 465,
    "MAIL_USE_TLS": False,
    "MAIL_USE_SSL": True,
    "MAIL_USERNAME": 'saranya.nukala1@gmail.com',
    "MAIL_PASSWORD": 'avlvsrksnmpjs'#password
}
app.config.update(mail_settings)
mail = Mail(app)

def email():
  u = User.query.all()
  t = date.today()
  for x in u:
    y = x.dob
    y = datetime.strptime(y,'%m/%d/%Y').date()
    y = y.replace(year = t.year)
    dif = y-t
    dif = dif.days
    if dif==-152:
      uf = Userfriends.query.filter_by(f1_id=x.social_id).all()
      for v in uf:
        m = User.query.filter_by(social_id=v.f2_id).one()
        msg = Message(subject="Hello",
                      sender=app.config.get("MAIL_USERNAME"),
                      recipients=[m.email], 
                      body="This is a test email I sent with Gmail and Python!"+str(dif)+str(m.nickname)+str(len(uf)))
        x = mail.send(msg)



if __name__ == '__main__':
  schedule.every(1).minutes.do(email)
  #schedule.every().day.at('08:00').do(email)
  while True:
        schedule.run_pending()
        time.sleep(1)
