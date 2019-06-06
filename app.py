from flask import Flask, redirect, url_for, render_template, flash, Response, request,jsonify
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user,login_required
from oauth import OAuthSignIn
from datetime import date,datetime
from flask_table import Table, Col,LinkCol,NestedTableCol
import json,re
from flask_wtf import FlaskForm
from flask_wtf.csrf import CsrfProtect
from wtforms import StringField,Form,validators
from wtforms.validators import DataRequired, Length,ValidationError

def create_app():
	app = Flask(__name__)
	return app

app= create_app()
bootstrap = Bootstrap(app)
app.config['SECRET_KEY'] = 'top secret!'
app.config['WTF_CSRF_ENABLED'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['OAUTH_CREDENTIALS'] = {
    'facebook': {
        'id': '1056706187870178',
        'secret': '48039bccdd0d0979e281c103c62fe543'
    }
}
db = SQLAlchemy(app)
lm = LoginManager(app)
lm.init_app(app)
lm.login_view = 'index'

class User(UserMixin, db.Model):
    __tablename__ = 'User'
    id = db.Column(db.Integer, primary_key=True)
    social_id = db.Column(db.String(64), nullable=False, unique=True)
    nickname = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(64), nullable=True)
    dob  =  db.Column(db.String(64), nullable=True)
    gender = db.Column(db.String(64), nullable = True)
    def __repr__(self):
    	return '{} - {}'.format(self.iso, self.nickname)
    def as_dict(self):
    	return {'nickname': self.nickname}
   
class Userfriends(db.Model):
	__tablename__ = 'Userfriends'
	id = db.Column(db.Integer, primary_key= True)
	f1_id = db.Column(db.String(64), nullable=False)
	f2_id = db.Column(db.String(64), nullable= False)
	close = db.Column(db.Boolean, default= False)
	
def validate_email(form,field):
	email = form.email.data
	user = User.query.filter_by(email=form.email.data).first()
	if len(email) > 7:
		if re.match("(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", email) != None:
			return True
		raise ValidationError('This is not a valid email address')

class UserForm(Form):
	email = StringField('email',validators=[DataRequired(), validate_email])

@app.route('/form')
def sdg():
	return render_template('search.html',x = names())

@app.route('/view/<nick>')
def view(nick):
	 n = db.session.query(User).filter_by(nickname=nick).one()
	 return n

def names():
	nick = user_friends()
	names=[]
	for x in nick:
		n = db.session.query(User).filter_by(social_id=x).one()
		names.append(n.nickname)
	return names

class Results(Table):
	id = Col('id')
	social_id = Col('social_id')
	nickname = Col('nickname')
	email = Col('email')
	dob = Col('Date of Birth')
	gender = Col('Gender')

class EditTable(Table):
	social_id = Col('social_id')
	nickname = Col('nickname')
	email = Col('email')
	dob = Col('Date of Birth')
	gender = Col('Gender')
	edit = LinkCol('Edit', 'edit')

class Resultfriends(Table):
	id = Col('id')
	f1_id = Col('f1_id')
	f2_id = Col('f2_id')
	close = Col('close')

@lm.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('index.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/authorize/<provider>')
def oauth_authorize(provider):
    if not current_user.is_anonymous:
        return redirect(url_for('index'))
    oauth = OAuthSignIn.get_provider(provider)
    return oauth.authorize()

@app.route('/results')# Users Database
def res():
	results =[]
	qry = db.session.query(User)
	results=qry.all()
	table = Results(results)
	table.border = True
	return render_template('results.html', table =table)

@app.route('/friend_list')#friendlist Database
def friend_list():
	results =[]
	qry = db.session.query(Userfriends)
	results=qry.all()
	table = Resultfriends(results)
	table.border = True
	return render_template('results.html', table =table)

@app.route('/edit',  methods=['GET', 'POST'])
def edit():
	query = db.session.query(User).filter_by(social_id= current_user.social_id)
	u = query.first()
	if u:
		form = UserForm(formdata=request.form, obj = u)
		if request.method =='POST' and form.validate():
			save_changes(u,form)
			return redirect('/')
		return render_template('edit.html',form = form)
	else:
		return 'Error Loading'

@app.route('/view_profile')
@login_required
def view_profile():
	results = []
	x = db.session.query(User).filter_by(social_id=current_user.social_id)
	results = x.all()
	table = EditTable(results)
	table.border = True
	return render_template('results.html',table = table)

def save_changes(u, form ):
	u.email = form.email.data
	db.session.commit()

def user_friends():
	nick =[]
	friend = db.session.query(Userfriends).filter_by(f1_id=current_user.social_id).all()
	for x in friend:
		nick.append(x.f2_id)
	return nick

@app.route('/friends')
def friends():
	if current_user.is_anonymous:
		return redirect(url_for('index'))
	else:
		nick =user_friends()
		u = []
		for x in nick:
			dob = []
			n = db.session.query(User).filter_by(social_id=x).one()
			dob.append(n.nickname)
			dob.append(n.dob)
			u.append(dob)
		#return "<h1>"+ni+"</h1>"
		return render_template('upcoming_birthdays.html',nick = u)
		
@app.route('/upcoming_birthdays')
def upcoming_birthdays():
	if current_user.is_anonymous:
		return redirect(url_for('index'))
	else:
		nick =user_friends()
		u = []
		t = date.today()
		for x in nick:
			dob = []
			n = db.session.query(User).filter_by(social_id=x).one()
			y = n.dob
			y = datetime.strptime(y,'%m/%d/%Y').date()
			y = y.replace(year = t.year)
			dif = y-t
			dif = dif.days
			if (dif<=15 and dif>=1):#do change dif<=15
				dob.append(n.nickname)
				dob.append(n.dob)
				u.append(dob)
		return render_template('upcoming_birthdays.html',nick = u)

@app.route('/today')
def today():
	if current_user.is_anonymous:
		return redirect(url_for('index'))
	else:
		nick =user_friends()
		u = []
		t = date.today()
		for x in nick:
			dob = []
			n =db.session.query(User).filter_by(social_id=x).one()
			y = n.dob
			y = datetime.strptime(y,'%m/%d/%Y').date()
			y = y.replace(year = t.year)
			dif = t-y
			dif = dif.days
			if (dif==0):#do change dif<=15
				dob.append(n.nickname)
				dob.append(y)
				u.append(dob)
		return render_template('upcoming_birthdays.html',nick = u)

@app.route('/callback/<provider>')
def oauth_callback(provider):
    if not current_user.is_anonymous:
        return redirect(url_for('index'))
    oauth = OAuthSignIn.get_provider(provider)
    social_id, username, email,dob, friend ,g= oauth.callback()
    if social_id is None:
        flash('Authentication failed.')
        return redirect(url_for('index'))
    user = User.query.filter_by(social_id=social_id).first()
    if not user:
        user = User(social_id=social_id, nickname=username, email=email, dob = dob , gender=g)
        db.session.add(user)
        db.session.commit()
    for x in range(len(friend)):
    	res = db.session.query(Userfriends).filter_by(f1_id=social_id,f2_id=friend[x]).all()
    	if not res:
    		f = Userfriends(f1_id= social_id,f2_id= friend[x] )
    		db.session.add(f)
    		db.session.commit()
    login_user(user, True)
    return redirect(url_for('index'))

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
