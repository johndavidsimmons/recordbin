from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from . import auth
from .. import db
from ..models import User
from .forms import (
	LoginForm, RegistrationForm, ChangePasswordForm,
	PasswordResetRequestForm, PasswordResetForm, ChangeEmailForm)
from ..email import send_email


@auth.route('/login', methods=["GET", "POST"])
def login():
	form = LoginForm()

	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		if user is not None and user.verify_password(form.password.data):
			login_user(user, form.remember_me.data)
			return redirect(request.args.get('next') or url_for("main.user", username=user.username))
		flash('invalid username or password', 'error')

	# if current_user.is_anonymous:
		# return render_template('auth/login.html', form=form)
	# else:
	return redirect(url_for('main.index'))


@auth.route('/logout')
@login_required
def logout():
	logout_user()
	flash('You have logged out', 'success')
	return redirect(url_for('main.index'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
	form = RegistrationForm()

	if form.validate_on_submit():
		user = User(
			email=form.email.data,
			password=form.password.data,
			username=form.username.data)
		db.session.add(user)
		user.add_self_follows()
		db.session.commit()
		user.add_self_follows()
		db.session.commit()
		token = user.generate_confirmation_token()
		send_email(
			user.email,
			'Confirm Your Account',
			'auth/email/confirm', user=user, token=token)
		flash('A confirmation email has been sent to {}.'.format(user.email), '')
		return redirect(url_for('auth.login'))

	if current_user.is_anonymous:
		return render_template('auth/register.html', form=form)
	else:
		return redirect(url_for('main.index'))


@auth.route('/confirm/<token>')
@login_required
def confirm(token):
	if current_user.confirmed:
		return redirect(url_for('main.index'))

	if current_user.confirm(token):
		flash('Thanks for confirming your account', 'success')
	else:
		flash('Your token is invalid or expired', 'error')

	return redirect(url_for('main.index'))


@auth.route('/confirm')
@login_required
def resend_confirmation():
	token = current_user.generate_confirmation_token()
	send_email(
		current_user.email,
		'Confirm Your Account',
		'auth/email/confirm', user=current_user, token=token)
	flash('A new confirmation email has been sent to you by email.', '')
	return redirect(url_for('main.index'))


@auth.before_app_request
def before_request():
	if current_user.is_authenticated:
		current_user.ping()
		if not current_user.confirmed \
			and request.endpoint[:5] != 'auth.' \
			and request.endpoint != 'static':
			return redirect(url_for('auth.unconfirmed'))


@auth.route('/unconfirmed')
def unconfirmed():
	if current_user.is_anonymous or current_user.confirmed:
		return redirect(url_for('main.index'))

	return render_template('auth/unconfirmed.html')


@auth.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
	form = ChangePasswordForm()

	if form.validate_on_submit():
		if current_user.verify_password(form.old_password.data):
			current_user.password = form.password.data
			db.session.add(current_user)
			db.session.commit()
			flash('Your password has been updated.', 'success')
			return redirect(url_for('main.edit_profile'))
		else:
			flash('invalid password', 'error')

	return render_template("auth/change_password.html", form=form)


@auth.route('/reset', methods=['GET', 'POST'])
def password_reset_request():
	if not current_user.is_anonymous:
		return redirect(url_for('main.index'))

	form = PasswordResetRequestForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		if user:
			token = user.generate_reset_token()
			send_email(
				user.email,
				'Reset Your Password',
				'auth/email/reset_password',
				user=user, token=token, next=request.args.get('next'))
			flash('An email with instructions has been sent to you.', 'success')
		else:
			flash('There is no account associated with that email address', 'error')

	return render_template('auth/reset_password_request.html', form=form)


@auth.route('/reset/<token>', methods=['GET', 'POST'])
def password_reset(token):
	if not current_user.is_anonymous:
		flash('you are is_anonymous', 'error')
		return redirect(url_for('main.index'))

	form = PasswordResetForm()

	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		if user is None:
			flash('user is None', 'error')
			return redirect(url_for('main.index'))
		if user.reset_password(token, form.password.data):
			flash('Your password has been updated', 'success')
			return redirect(url_for('auth.login'))
		else:
			flash('Something went wrong, password not updated', 'error')
			return redirect(url_for('main.index'))

	return render_template('auth/reset_password.html', form=form)


@auth.route('/change-email', methods=['GET', 'POST'])
@login_required
def change_email_request():
	form = ChangeEmailForm()

	if form.validate_on_submit():
		if current_user.verify_password(form.password.data):
			new_email = form.email.data
			token = current_user.generate_email_change_token(new_email)
			send_email(
				new_email,
				'Confirm your email address',
				'auth/email/change_email', user=current_user, token=token)
			flash('An email with instructions to confirm your new email \
				address has been sent to {}'.format(new_email), 'success')
			return redirect(url_for('main.index'))
		else:
			flash('Invalid email or password.', 'error')
	return render_template("auth/change_email.html", form=form)


@auth.route('/change-email/<token>', methods=['GET', 'POST'])
@login_required
def change_email(token):
	if current_user.change_email(token):

		flash('Your email address has been updated.', 'success')
	else:
		flash('Invalid request. Bad Token', 'error')
	return redirect(url_for('main.index'))
