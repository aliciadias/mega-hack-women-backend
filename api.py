import os
import jwt
import time

from flask import Flask, abort, request, jsonify, g, url_for, render_template, session
from sqlalchemy import or_
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mega-hack-women' # example secret key **please use a real working one on production
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite' #example URI
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True

cors = CORS(app, resources=r'/api/*')
db = SQLAlchemy(app)
auth = HTTPBasicAuth()

class User(db.Model):
	__tablename__ = 'users'
	id = db.Column(db.Integer, primary_key=True)
	password_hash = db.Column(db.String(64))
	name = db.Column(db.String(50))
	email = db.Column(db.String(50), index=True)
	formal = db.Column(db.Boolean)
	business = db.Column(db.String(50), nullable=True, index=True)
	area = db.Column(db.String(50), nullable=True, index=True)
	desc = db.Column(db.String(800), nullable=True)
	schedule = db.Column(db.String(80), nullable=True)

	def hash(self, password):
		self.password_hash = generate_password_hash(password)

	def check_password(self, password):
		return check_password_hash(self.password_hash, password)

	def create_token(self, expires_in=600000):
		return jwt.encode(
			{'id': self.id, 'exp': time.time() + expires_in},
			app.config['SECRET_KEY'], algorithm='HS256'
		)

	@staticmethod
	def check_token(token):
		try:
			data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
		except:
			return
		return User.query.get(data['id'])


@auth.verify_password
def check_password(user_or_token, password):
	user = User.check_token(user_or_token)

	if not user:
		user = User.query.filter_by(email=user_or_token).first()

		if not user or not user.check_password(password):
			return False
	g.user = user
	return True


@app.route('/api/users/<int:id>', methods=['POST', 'GET'])
def get_user(id):
	user = User.query.get(id)

	if not user:
		abort(400) #doesn't exist
	
	return jsonify({'name': user.name, 'id': user.id, 'formal': user.formal, 
					'desc':user.desc, 'schedule': user.schedule,
					'business': user.business, 'area': user.area})


@app.route('/api/token/<string:email>')
@auth.login_required
def get_token(email):
	token = g.user.create_token(600000)
	user = User.query.filter_by(email=email).first()
	return jsonify({'token': token.decode('ascii'), 'duration': 600000, 'id': user.id})


@app.route('/api/filter_users', methods=['PUT'])
def filter_users():
	business_filter = request.json.get("data").get("business")
	area_filter = request.json.get("data").get("area")

	matches = []

	if area_filter is not None and business_filter is not None:
		users = User.query.filter(
			User.formal == True
		).filter(
			User.business == business_filter
		).filter(
			User.area == area_filter
		).all()

	elif area_filter is None and business_filter is not None:
		users = User.query.filter(
			User.formal == True
		).filter(
			User.business == business_filter
		).all()
	elif business_filter is None and area_filter is not None:
		users = User.query.filter(
			User.formal == True
		).filter(
			User.area == area_filter
		).all()
	else:
		users = User.query.filter(User.formal == True).all()

	if users:		
		for user in users:
			matches.append({'name': user.name, 'id': user.id, 'business': user.business, 'area': user.area, "desc": user.desc})
	
	return jsonify(matches)


@app.route('/api/user_email/<int:id>', methods=['GET'])
def get_email(id):
	user = User.query.get(id)
	email = user.email

	return jsonify([email])


@app.route('/api/all_users', methods=['GET'])
@auth.login_required
def get_all_users():
	users = User.query.filter(User.formal == True).all()
	matches = []

	if users:
		for user in users:
			matches.append({'name': user.name, 'id': user.id, 'business': user.business,
						'area': user.area, "desc": user.desc})

	return jsonify(matches)

@app.route('/api/full_match/<int:id>', methods=['PUT'])
def get_best_user(id):

	r_user = User.query.get(id)
	desired_business = request.json.get("data").get("business")
	desired_area = request.json.get("data").get("area")
	user_business = r_user.business
	user_area = r_user.area
	matches = []

	if desired_business is not None:
		user_business = desired_business
	if desired_area is not None:
		user_area = desired_area
	
	best_match = User.query.filter(
		User.id != id,
		User.formal == True,
		User.business == user_business,
		User.area == user_area
	).limit(3).all()
	print(best_match)	
	if best_match:
		for user in best_match:
			matches.append({'name': user.name, 'id': user.id, 'business': user.business, 'area': user.area, "desc": user.desc})
	else:
		best_match = User.query.filter(
			User.id != id,
			User.formal == True
		).filter(
			or_(
				User.business == user_business,
				User.area == user_area
			)
		).limit(3).all()
		if best_match:
			for user in best_match:
				matches.append({'name': user.name, 'id': user.id, 'business': user.business, 'area': user.area, "desc": user.desc})
		else:
			best_match = User.query.filter(User.id != id, User.formal == True).limit(3).all()
			for user in best_match:
				matches.append({'name': user.name, 'id': user.id, 'business': user.business, 'area': user.area, "desc": user.desc})

	return jsonify(matches)


@app.route('/api/profile/edit/<int:id>', methods=['PUT'])
@auth.login_required
def update_description(id):
	description = request.json.get('desc')
	business = request.json.get('business')
	area = request.json.get('area')
	user = User.query.get(id)
	user.desc = description
	user.business = business
	user.area = area

	db.session.commit()

	return jsonify({'id':user.id,'desc':user.desc, 'business': user.business, 'area': user.area})


@app.route('/api/users', methods=['POST'])
def new_user():
	name = request.json.get('name')
	password = request.json.get('password')
	email = request.json.get('email')
	formal = request.json.get('formal')
	business = request.json.get('business')
	area = request.json.get('area')

	if email is None or password is None:
		abort(400) #missing **kargs

	if User.query.filter_by(email=email).first() is not None:
		abort(401) # user already exists

	user = User(name=name, email=email, formal=formal, desc=None, schedule=None, business=business, area=area)
	user.hash(password)
	db.session.add(user)
	db.session.commit()
	
	return (jsonify({'email': user.email}), 201,
					{'Location': url_for('get_user', id=user.id, _external=True)})


if __name__=='__main__':
	if not os.path.exists('db.sqlite'):
		db.create_all()
	app.run(debug=False)
