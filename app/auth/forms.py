from flask_wtf import Form
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import Required, Length, Email, Regexp, EqualTo, NoneOf
from wtforms import ValidationError
from ..models import User

forbidden_usernames = [
	"users", "login", "register",
	"home", "index", "/", "edit-profile",
	"auth", "auth/", "edit-profile/", "about"]


class LoginForm(Form):

	email = StringField('Email', validators=[
		Required(message="Email is required"),
		Email(message="Invalid email address")])

	password = PasswordField('Password', validators=[
		Required(message="Password is required")])

	remember_me = BooleanField('Remember Me')


class RegistrationForm(Form):

	username = StringField('Username', validators=[
		Required(message="Username is required"),
		Length(min=3, max=63, message="Usernames must be between 3-64 characters"),
		Regexp(
			'^[A-Za-z0-9]', 0,
			'Usernames can only contain letters and numbers'
		),
		NoneOf(
			[x.lower() for x in forbidden_usernames],
			message="Please choose a different username")])

	email = StringField('Email', validators=[
		Required(message="Email is required"), 
		Length(1, 63, message="Email addresses must be between 3-64 characters"),
		Email(message="Invalid email address")])

	password = PasswordField('Password', validators=[
		Required(message="Password is required"),
		Length(min=8, max=64, message="Passwords must be between 8-64 characters"),
		EqualTo('password2', message='Passwords must match.')])

	password2 = PasswordField('Confirm password', validators=[
		Required(message="Password match is required")])

	def validate_email(self, field):
		"""Test that email address is not already registered"""
		if User.query.filter_by(email=field.data).first():
			raise ValidationError('Email already registered.')

	def validate_username(self, field):
		"""Test that username not already registered"""
		if User.query.filter_by(username=field.data).first():
			raise ValidationError('Username already registered.')


class ChangePasswordForm(Form):

	old_password = PasswordField('Old password', validators=[
		Required()])

	password = PasswordField('New password', validators=[
		Required(), EqualTo('password2', message='Passwords must match')])

	password2 = PasswordField('Confirm new password', validators=[
		Required()])


class PasswordResetRequestForm(Form):
	email = StringField('Email', validators=[Required(), Email()])


class PasswordResetForm(Form):
	email = StringField('Email', validators=[
		Required(), Email()])

	password = PasswordField('New Password', validators=[
		Required(), EqualTo('password2', message='Passwords must match')])

	password2 = PasswordField('Confirm Password', validators=[
		Required()])

	def validate_email(self, field):
		"""Test that the email address is registered"""
		if User.query.filter_by(email=field.data).first() is None:
			raise ValidationError('Unknown email address')


class ChangeEmailForm(Form):

	email = StringField('New Email', validators=[
		Required(), Length(1, 64), Email()])

	password = PasswordField('Password', validators=[Required()])

	def validate_email(self, field):
		"""Test that the new email address isn't already registered"""
		if User.query.filter_by(email=field.data).first():
			raise ValidationError('Email already registered.')
