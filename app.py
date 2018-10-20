from flask_login import LoginManager, login_user, current_user, login_required, logout_user, UserMixin
from flask import Flask,jsonify,request,render_template,Response,flash,redirect,url_for
from flask_restless import APIManager
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_wtf import Form
from wtforms import TextField, BooleanField, validators, PasswordField, SubmitField, SelectField, FileField, SelectMultipleField, BooleanField, DateField
from werkzeug.security import generate_password_hash, \
	 check_password_hash
import datetime
from sqlalchemy import create_engine
#from wtforms.validators import Required
from werkzeug.utils import secure_filename
import os
import uuid

import requests
import datetime

app = Flask(__name__)

app.config.update(dict(
	SECRET_KEY="powerful secretkey",
	WTF_CSRF_SECRET_KEY="a csrf secret key"
))

def getLocations():
	return ['london, england', 'austin, texas', 'cancun, mexico']

def time_utc_to_english(time):
	return datetime.datetime.strptime(time, '%Y-%m-%dT%H:%M:%S').strftime("%B %d, %Y at %H:%M")

def get_events(location, start, end):
	return requests.get(
	    "https://www.eventbriteapi.com/v3/events/search?sort_by=best&location.address=" + location
	    + '&start_date.range_start=' + start + '&start_date.range_end=' + end,
	    headers = {
	        "Authorization": "Bearer 7PW4452MWTLYVZVWNH3K",
	    },
	    verify = True,  # Verify SSL certificate
	)


class SearchForm(Form):
	budget = TextField('Budget', [validators.Required()], id='select_budget')
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

@app.route('/', methods=['GET', 'POST'])
def home():
	form = SearchForm()
	if form.validate_on_submit():
		if form.validate():
			print('initial validation')
			return redirect('/dashboard?start=' + form.start.data.strftime('%Y-%m-%dT00:00:00') + '&end=' + form.end.data.strftime('%Y-%m-%dT23:59:59'))
		else:
			flash("Please make sure your budget is above $0.00 and your start date is before your end date.", category='red')
	return render_template('index.html', form=form)

@app.route('/dashboard')
def dash():
	start = request.args.get('start')
	end = request.args.get('end')
	locations = getLocations()
	dashdata = list()
	for location in locations:
		events = get_events(location, start, end).json()
		dashdata.append(events)
	return render_template('dashboard.html', data=dashdata)


if __name__ == "__main__":
	app.run(host="0.0.0.0", debug=True)
	#app.run(host='0.0.0.0', port=80)