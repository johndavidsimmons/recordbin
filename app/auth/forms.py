from flask_wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import Required, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from ..models import User


class LoginForm(Form):
	email = StringField('Email', validators=[Required(), Email()])
	password = PasswordField('Password', validators=[Required()])
	remember_me = BooleanField('Remember Me')

class RegistrationForm(Form):
	username = StringField('Username', validators=[
		Required(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
										  'Usernames must have only letters, '
										  'numbers, dots or underscores')])
	email = StringField('Email', validators=[Required(), Length(1, 64),
										   Email()])
	password = PasswordField('Password', validators=[
		Required(), EqualTo('password2', message='Passwords must match.')])
	password2 = PasswordField('Confirm password', validators=[Required()])

	def validate_email(self, field):
		if User.query.filter_by(email=field.data).first():
			raise ValidationError('Email already registered.')

class ChangePasswordForm(Form):
	old_password = PasswordField('Old password', validators=[Required()])
	password = PasswordField('New password', validators=[Required(), EqualTo('password2', message='Passwords must match')])
	password2 = PasswordField('Confirm new password', validators=[Required()])

class PasswordResetRequestForm(Form):
	email = StringField('Email', validators=[Required(), Email()])    

class PasswordResetForm(Form):
	email = StringField('Email', validators=[Required(), Email()])
	password = PasswordField('New Password', validators=[Required(), EqualTo('password2', message='Passwords must match')])
	password2 = PasswordField('Confirm Password', validators=[Required()])

	def validate_email(self, field):
		if User.query.filter_by(email=field.data).first() is None:
			raise ValidationError('Unknown email address')

class ChangeEmailForm(Form):
	email = StringField('New Email', validators=[Required(), Length(1, 64),Email()])
	password = PasswordField('Password', validators=[Required()])

	def validate_email(self, field):
		if User.query.filter_by(email=field.data).first():
			raise ValidationError('Email already registered.')







