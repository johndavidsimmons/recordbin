from . import db
from . import login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, AnonymousUserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app, request
import hashlib
from datetime import datetime
from dateutil import tz
import os
import base64


def gravatar(email, size=100, default='identicon', rating='g'):
	if request.is_secure:
		url = 'https://secure.gravatar.com/avatar'
	else:
		url = 'http://www.gravatar.com/avatar'

	hash = hashlib.md5(email.encode('utf-8')).hexdigest()

	return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
		url=url, hash=hash, size=size, default=default, rating=rating)


def user_local_time(utctime):
	from_zone = tz.tzutc()
	to_zone = tz.tzlocal()
	utc_string = str(datetime.utcnow()).split('.').pop(0)
	utc = datetime.strptime(utc_string, '%Y-%m-%d %H:%M:%S')
	utc = utc.replace(tzinfo=from_zone)
	user_time = utc.astimezone(to_zone)
	return user_time


def encode_id(string):
	key = os.environ.get('SECRET_KEY')
	string = str(string)
	encoded_chars = []
	for i in range(len(string)):
		key_c = key[i % len(key)]
		encoded_c = chr(ord(string[i]) + ord(key_c) % 256)
		encoded_chars.append(encoded_c)
	encoded_string = "".join(encoded_chars)
	return base64.urlsafe_b64encode(encoded_string)


def decode_id(string):
	key = os.environ.get('SECRET_KEY')
	decoded_chars = []
	string = base64.urlsafe_b64decode(string)
	for i in range(len(string)):
		key_c = key[i % len(key)]
		encoded_c = chr(abs(ord(string[i]) - ord(key_c) % 256))
		decoded_chars.append(encoded_c)
	decoded_string = "".join(decoded_chars)
	return int(decoded_string.encode('ascii', 'ignore'))


class Permission:
	ADMINISTER = 0x80
	USE = 0x01


class Role(db.Model):
	__tablename__ = 'roles'
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(64), unique=True)
	default = db.Column(db.Boolean, default=False, index=True)
	permissions = db.Column(db.Integer)

	# FK & Relationship
	users = db.relationship('User', backref='role', lazy='dynamic')

	@staticmethod
	def insert_roles():
		roles = {
			'user': (Permission.USE, True),
			'admin': (Permission.ADMINISTER, False)
		}

		for r in roles:
			role = Role.query.filter_by(name=r).first()
			if role is None:
				role = Role(name=r)
			role.permissions = roles[r][0]
			role.default = roles[r][1]
			db.session.add(role)
			db.session.commit()

	# Methods
	def __init__(self, name):
		self.name = name

	def __repr__(self):
		return '<Role {}>'.format(self.name)


class Follow(db.Model):
	__tablename__ = 'follows'
	follower_id = db.Column(db.Integer, db.ForeignKey('users_table.id'), primary_key=True)
	followed_id = db.Column(db.Integer, db.ForeignKey('users_table.id'), primary_key=True)
	timestamp = db.Column(db.DateTime, default=datetime.utcnow)


class User(UserMixin, db.Model):
	__tablename__ = 'users_table'
	id = db.Column(db.Integer, primary_key=True)
	email = db.Column(db.String(64), unique=True, index=True)
	username = db.Column(db.String(64), unique=True, index=True)
	password_hash = db.Column(db.String(128))
	confirmed = db.Column(db.Boolean, default=False)
	name = db.Column(db.String(64))
	location = db.Column(db.String(64))
	about_me = db.Column(db.Text())
	member_since = db.Column(db.DateTime(), default=datetime.utcnow)
	last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
	avatar_hash = db.Column(db.String(32))
	migrate_test = db.Column(db.String(32))

	# FK & Relationship
	role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), default=2)
	followed = db.relationship(
		'Follow',
		foreign_keys=[Follow.follower_id],
		backref=db.backref('follower', lazy='joined'),
		lazy='dynamic',
		cascade='all, delete-orphan')
	followers = db.relationship(
		'Follow',
		foreign_keys=[Follow.followed_id],
		backref=db.backref(
			'followed', lazy='joined'), lazy='dynamic', cascade='all, delete-orphan')

	def gravatar(self, size=100, default='identicon', rating='g'):
		if request.is_secure:
			url = 'https://secure.gravatar.com/avatar'
		else:
			url = 'http://www.gravatar.com/avatar'

		hash = hashlib.md5(self.email.encode('utf-8')).hexdigest()

		return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
			url=url, hash=hash, size=size, default=default, rating=rating)

	def follow(self, user):
		if not self.is_following(user):
			f = Follow(follower=self, followed=user)
			db.session.add(f)
			db.session.commit()

	def unfollow(self, user):
		f = self.followed.filter_by(followed_id=user.id).first()
		if f:
			db.session.delete(f)
			db.session.commit()

	def is_following(self, user):
		return self.followed.filter_by(
			followed_id=user.id).first() is not None

	def is_followed_by(self, user):
		return self.followers.filter_by(
			follower_id=user.id).first() is not None

	def owned_records(self):
		return Title.query.join(
			Artist, Title.artist_id == Artist.id) \
			.join(Size, Title.size_id == Size.id) \
			.join(Format, Title.format_id == Format.id) \
			.add_columns(Artist.name, Size.name, Format.name, Title.mail) \
			.filter(Title.owner_id == self.id).all()

	def follower_records(self):
		return Title.query.join(
			Follow, Follow.followed_id == Title.owner_id) \
			.join(User, Follow.followed_id == User.id) \
			.join(Artist, Title.artist_id == Artist.id) \
			.add_columns(User.email, Artist.name, User.username) \
			.filter(Follow.follower_id == self.id).order_by(Title.timestamp.desc())

	def __init__(self, **kwargs):
		super(User, self).__init__(**kwargs)
		if self.role is None:
			if self.email == current_app.config['RECORDBIN_ADMIN']:
				self.role = Role.query.filter_by(name='admin').first()
			if self.role is None:
				self.role = Role.query.filter_by(name='user').first()
		if self.email is not None and self.avatar_hash is None:
			self.avatar_hash = hashlib.md5(self.email.encode('utf-8')).hexdigest()

	def change_email(self, token):
		s = Serializer(current_app.config['SECRET_KEY'])
		try:
			data = s.loads(token)
		except:
			return False
		if data.get('change_email') != self.id:
			return False
		new_email = data.get('new_email')
		if new_email is None:
			return False
		if self.query.filter_by(email=new_email).first() is not None:
			return False
		self.email = new_email
		self.avatar_hash = hashlib.md5(self.email.encode('utf-8')).hexdigest()
		db.session.add(self)
		db.session.commit()
		return True

	def generate_email_change_token(self, new_email, expiration=3600):
		s = Serializer(current_app.config['SECRET_KEY'], expiration)
		return s.dumps({'change_email': self.id, 'new_email': new_email})

	@staticmethod
	def add_self_follows():
		for user in User.query.all():
			if not user.is_following(user):
				user.follow(user)
				db.session.add(user)
				db.session.commit()

	@property
	def password(self):
		raise AttributeError('Password is not a readable attribute')

	def can(self, permissions):
		return self.role is not None and (self.role.permissions & permissions) == permissions

	def is_administrator(self):
		return self.can(Permission.ADMINISTER)

	def ping(self):
		self.last_seen = datetime.utcnow()
		db.session.add(self)
		db.session.commit()

	@password.setter
	def password(self, password):
		self.password_hash = generate_password_hash(password)

	def verify_password(self, password):
		return check_password_hash(self.password_hash, password)

	def __repr__(self):
		return '<User {}>'.format(self.email)

	def generate_confirmation_token(self, expiration=3600):
		s = Serializer(current_app.config['SECRET_KEY'], expiration)
		return s.dumps({'confirm': self.id})

	def confirm(self, token):
		s = Serializer(current_app.config['SECRET_KEY'])
		try:
			data = s.loads(token)
		except:
			return False
		if data.get('confirm') != self.id:
			return False
		self.confirmed = True
		db.session.add(self)
		db.session.commit()
		return True

	def generate_reset_token(self, expiration=3600):
		s = Serializer(current_app.config['SECRET_KEY'], expiration)
		return s.dumps({'reset': self.id})

	def reset_password(self, token, new_password):
		s = Serializer(current_app.config["SECRET_KEY"])
		try:
			data = s.loads(token)
		except:
			return False
		if data.get('reset') != self.id:
			return False
		self.password = new_password
		db.session.add(self)
		db.session.commit()
		return True

	@staticmethod
	def generate_fake(count=100):
		from sqlalchemy.exc import IntegrityError
		from random import seed
		import forgery_py

		seed()
		for i in range(count):
			u = User(
				email=forgery_py.internet.email_address(),
				username=forgery_py.internet.user_name(True),
				password=forgery_py.lorem_ipsum.word(),
				confirmed=True, name=forgery_py.name.full_name(),
				location=forgery_py.address.city(),
				about_me=forgery_py.lorem_ipsum.sentence(),
				member_since=forgery_py.date.date(True))
			db.session.add(u)
			try:
				db.session.commit()
			except IntegrityError:
				db.session.rollback()

	@staticmethod
	def to_json(self):
		json_user = {
			"ID": self.id,
			'username': self.username,
			"email": self.email,
			'member_since': self.member_since,
			'last_seen': self.last_seen,
			"owned_record_count": len(self.owned_records()),
			"users_following:": len(self.followed.all()),
			"users_followed_by": len(self.followers.all()),
			"name": self.name,
			"about_me": self.about_me
		}

		return json_user

	@staticmethod
	def record_count(self):
		return len(self.owned_records())


class Title(db.Model):
	__tablename__ = 'titles'
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(64), index=True)
	artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'))
	size_id = db.Column(db.Integer, db.ForeignKey('sizes.id'))
	color = db.Column(db.String(64))
	year = db.Column(db.Integer)
	format_id = db.Column(db.Integer, db.ForeignKey('formats.id'), default=1)
	notes = db.Column(db.String(128))
	timestamp = db.Column(db.DateTime, default=user_local_time(datetime.utcnow))
	owner_id = db.Column(db.Integer, db.ForeignKey('users_table.id'))
	mail = db.Column(db.Integer, default=0)

	# Methods
	def __init__(
		self, name, artist_id, year, format_id, owner_id, mail,
		size_id=None, color=None, notes=None):
		self.name = name
		self.artist_id = artist_id
		self.year = year
		self.format_id = format_id
		self.owner_id = owner_id
		self.size_id = size_id
		self.color = color
		self.notes = notes
		self.mail = mail

	def add_to_table(self):
		db.session.add(self)
		db.session.commit()

	def delete_from_table(self):
		db.session.delete(self)
		db.session.commit()

	def update_from_mail(self):
		if self.mail == 1:
			self.mail = 0
			self.timestamp = datetime.now()
			db.session.add(self)
			db.session.commit()

	def to_json(self):
		json_title = {
			"name": self.name,
			"artist_id": self.artist_id,
			"year": self.year,
			"format_id": self.format_id,
			"owner_id": self.owner_id,
			"size_id": self.size_id,
			"color": self.color,
			"notes": self.notes,
			"mail": self.mail
		}

		return json_title

	def __repr__(self):
		return '<Title: {}>'.format(self.name)


class Size(db.Model):
	__tablename__ = 'sizes'
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.Integer, unique=True)

	# Methods
	def __init__(self, name):
		self.name = name

	def __repr__(self):
		return '<Size {}>'.format(self.name)

	@staticmethod
	def insert_sizes():
		sizes = [7, 10, 12]

		for s in sizes:
			db.session.add(Size(name=s))
			db.session.commit()


class Format(db.Model):
	__tablename__ = 'formats'
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(64), unique=True)

	# Methods
	def __init__(self, name):
		self.name = name

	def __repr__(self):
		return '<Format {}>'.format(self.name)

	@staticmethod
	def insert_formats():
		formats = ['vinyl']

		for f in formats:
			db.session.add(Format(name=f))
			db.session.commit()


class Artist(db.Model):
	__tablename__ = 'artists'
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(64), unique=True)

	# FK & Relationship

	# Methods
	def __init__(self, name):
		self.name = name

	def __repr__(self):
		return '<Artist {}>'.format(self.name)

	def add_to_table(self):
		db.session.add(self)
		db.session.commit()

	def delete_from_table(self):
		db.session.delete(self)
		db.session.commit()


class AnonymousUser(AnonymousUserMixin):
	def can(self, permissions):
		return False

	def is_administrator(self):
		return False


@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))

# make changes -> migrate -> upgrade
	# python manage.py db migrate -m 'default role id'
	# python manage.py db upgrade

# Title.query.join(Artist).filter(Artist.id==Title.artist_id).all()
