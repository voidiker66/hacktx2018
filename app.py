from flask_login import LoginManager, login_user, current_user, login_required, logout_user, UserMixin
from flask import Flask,jsonify,request,render_template,Response,flash,redirect,url_for
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_wtf import Form
from wtforms import TextField, BooleanField, validators, PasswordField, SubmitField, SelectField, FileField, SelectMultipleField, BooleanField, DateField
from werkzeug.security import generate_password_hash, \
	 check_password_hash
import datetime
from sqlalchemy import create_engine
from flask_restless import APIManager
#from wtforms.validators import Required
from werkzeug.utils import secure_filename
import os
import uuid

import requests
import datetime
import copy

import airlines

app = Flask(__name__)
db = SQLAlchemy(app)

app.config.update(dict(
	SECRET_KEY="powerful secretkey",
	WTF_CSRF_SECRET_KEY="a csrf secret key"
))

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database/dream.db'

e = create_engine('sqlite:///database/dream.db')

login_manager = LoginManager()


@login_manager.user_loader
def get_user(ident):
  return User.query.get(int(ident))

class User(db.Model, UserMixin):
	__tablename__ = 'User'
	id = db.Column(db.Integer, primary_key = True)
	username = db.Column(db.String(32))
	firstname = db.Column(db.String(32))
	lastname = db.Column(db.String(32))
	email = db.Column(db.String(32))
	password = db.Column(db.String(32))

	def __init__(self, username, firstname, lastname, email, password):
		self.username = username
		self.set_password(password)
		self.email = email
		self.firstname = firstname
		self.lastname = lastname

	def set_password(self, password):
		self.password = generate_password_hash(password)

	def check_password(self, password):
		return check_password_hash(self.password, password)
		#return password == self.password

class LoginForm(Form):
	username = TextField('Username', [validators.Required()])
	password = PasswordField('Password', [validators.Required()])
	submit = SubmitField('Log In')

	def __init__(self, *args, **kwargs):
		Form.__init__(self, *args, **kwargs)
		self.user = None

	def validate(self):
		user = User.query.filter_by(
			username=self.username.data).first()
		if user is None:
			self.username.errors.append('Unknown username')
			return False

		if not user.check_password(self.password.data):
			self.password.errors.append('Invalid password')
			return False

		self.user = user
		login_user(user)
		return True

class RegisterForm(Form):
	username = TextField('Username', validators=[validators.Required()])
	email = TextField('E-Mail', validators=[validators.Required(), validators.Email()])
	password = PasswordField('Password', [
		validators.Required(),
		validators.EqualTo('confirm', message='Passwords must match')
	])
	confirm = PasswordField('Repeat Password')
	firstname = TextField('First Name', validators=[validators.Required(), validators.Length(min=8, max=32, message="Password must be between 8 and 32 characters long")])
	lastname = TextField('Last Name', validators=[validators.Required()])
	submit = SubmitField('Submit')

	def __init__(self, *args, **kwargs):
		Form.__init__(self, *args, **kwargs)

	def validate(self):
		if self.username.data and self.password.data and self.confirm.data:
			if User.query.filter_by(username=self.username.data).first():
				flash('An account with that username already exists.', category='red')
				return False
			if User.query.filter_by(email=self.email.data).first():
				flash('An account with that email already exists.', category='red')
				return False
			return True
		return False

@app.route('/login', methods=['GET', 'POST'])
def login():
	form = LoginForm()
	if form.validate_on_submit():
		if form.validate():
			# flash("You're now logged in!", category='green')
			return redirect('/')
		else:
			flash("No user with that email/password combo", category='red')
	return render_template('login.html', form=form)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
	form = RegisterForm()
	if form.validate_on_submit():
		if form.validate():
			user = User(form.username.data, form.firstname.data, form.lastname.data, form.email.data, form.password.data)
			db.session.add(user)
			db.session.commit()
			flash("You're now registered!", category='green')
			return redirect('/login')
		else:
			flash("Error: Check your inputs", category='red')
	return render_template('register.html', form=form)

@app.route("/logout")
@login_required
def logout():
	logout_user()
	return redirect('/')

def get_currency():
	return ['USD', 'EUR', 'CNY']

def time_utc_to_english(time):
	return datetime.datetime.strptime(time, '%Y-%m-%dT%H:%M:%S').strftime("%B %d, %Y at %H:%M")

def get_events(location, start, end):
	return requests.get(
	    "https://www.eventbriteapi.com/v3/events/search?sort_by=date&location.address=" + location
	    + '&start_date.range_start=' + start.replace(' ', 'T') + '&start_date.range_end=' + end.replace(' ', 'T'),
	    headers = {
	        "Authorization": "Bearer 7PW4452MWTLYVZVWNH3K",
	    },
	    verify = True,  # Verify SSL certificate
	)


class SearchForm(Form):
	budget = TextField('Budget', [validators.Required()], id='select_budget')
	currency = SelectField('Currency', [validators.Required()], id='select_currency', default="Currency")
	cities = SelectField('Departure City', validators=[validators.Required()], id='select_cities')
	start = DateField('Start', validators=[validators.Required()], id='select_start', format='%m/%d/%Y', default=datetime.datetime.now())
	end = DateField('End', validators=[validators.Required()], id='select_end', format='%m/%d/%Y', default=datetime.datetime.now() + datetime.timedelta(days=1))
	submit = SubmitField('Let\'s Go!')

	def __init__(self, *args, **kwargs):
		Form.__init__(self, *args, **kwargs)

	def validate(self):
		if self.budget.data and self.start.data and self.end.data:
			if self.start.data > self.end.data or float(self.budget.data) < 0.0:
				return False
			return True
		return False

@app.route('/profile')
@login_required
def profile():
	return render_template('profile.html')

@app.route('/events')
def events():
	city_from = request.args.get('from')
	city_to = request.args.get('to')
	start = datetime.datetime.strptime(request.args.get('start'), '%Y-%m-%dT%H:%M:%S')
	end = datetime.datetime.strptime(request.args.get('end'), '%Y-%m-%dT%H:%M:%S')
	total_days = (end - start).days + 1
	events = dict()
	start_of_day = start.replace(hour=0, minute=0, second=0)
	end_of_day = start.replace(hour=23, minute=59, second=59)
	events[0] = get_events(city_to, str(start), str(end_of_day)).json()
	for index in range(1, total_days-1):
		start_of_day = start_of_day + datetime.timedelta(days=1)
		end_of_day = end_of_day + datetime.timedelta(days=1)
		events[index] = get_events(city_to, str(start_of_day), str(end_of_day)).json()
	events[total_days - 1] = get_events(city_to, str(start_of_day + datetime.timedelta(days=1)), str(end)).json()
	data = {'city_from': city_from, 'city_to': city_to, 'start': start, 'end': end, 'total_days': total_days, 'events': events}
	return render_template('events.html', data=data)

@app.route('/', methods=['GET', 'POST'])
def home():
	form = SearchForm()
	form.cities.choices = [(city, city) for city in airlines.get_cities_names()]
	form.currency.choices = [(cur, cur) for cur in get_currency()]
	if form.validate_on_submit():
		if form.validate():
			print('initial validation')
			return redirect('/dashboard?origin=' + form.cities.data + '&start=' + form.start.data.strftime('%Y-%m-%dT00:00:00') + '&end=' + form.end.data.strftime('%Y-%m-%dT23:59:59'))
		else:
			flash("Please make sure your budget is above $0.00 and your start date is before your end date.", category='red')
	return render_template('index.html', form=form)

@app.route('/dashboard')
def dash():
	start = request.args.get('start')
	end = request.args.get('end')
	locations = airlines.get_cities_names()
	dashdata = list()
	for location in locations:
		events = get_events(location, start, end).json()
		dashdata.append(events)
	return render_template('dashboard.html', data=dashdata)

@app.route('/flight')
def flight():
        origin = request.args.get('origin')
        destination = request.args.get('destination')
        start_date = request.args.get('start')
        end_date = request.args.get('end')
        return render_template('flight.html', flights= \
            airlines.get_flights_view(airlines.get_dest_flights( \
            origin=origin, destination=destination, start_date=start_date, \
            end_date=end_date)), retFlights=airlines.get_flights_view( \
            airlines.get_return_flights(origin=origin, destination=destination, \
            start_date=start_date, end_date=end_date)))

@app.route('/confirm')
def confirm():
	return render_template('confirm.html')


@login_manager.unauthorized_handler
def unauthorized_callback():
	return redirect('/login')


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

login_manager.init_app(app)

if __name__ == "__main__":
	app.run(host="0.0.0.0", debug=True)
	#app.run(host='0.0.0.0', port=80)
