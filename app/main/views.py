from flask import (
	render_template, redirect, url_for,
	current_app, abort, flash, request, jsonify, make_response)
from flask_login import login_required, current_user, login_user
from .. import db
from ..models import (
	User, Role, Artist, Title,
	Size, Format, gravatar, user_local_time, encode_id, decode_id, Image)
from . import main
from .forms import EditProfileForm, EditProfileAdminForm, AddRecordForm, EditRecordForm
from ..decorators import admin_required
from datetime import datetime
from ..auth.forms import LoginForm
import urlparse
from ..email import send_email


@main.route('/users', methods=['GET', 'POST'])
def all_users():
	all_users = sorted(User.query.all(), key=lambda x: x.username)
	return render_template('users.html', all_users=all_users)


@main.route('/shutdown')
def server_shutdown():
	if not current_app.testing:
		abort(404)
	shutdown = request.environ.get('werkzeug.server.shutdown')

	if not shutdown:
		abort(500)
	shutdown()

	return 'Shutting down...'

@main.route('/', methods=['GET', 'POST'])
def index():

	if current_user.is_authenticated:
		return redirect(url_for("main.user", username=current_user.username))

	form = LoginForm()

	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		if user is not None and user.verify_password(form.password.data):
			login_user(user, remember=form.remember_me.data)
			return redirect(request.args.get('next') or url_for("main.user", username=user.username))
		flash('invalid username or password', 'error')		
	return render_template('index.html', form=form)


@main.route('/<username>', methods=["GET", "POST"])
def user(username):
	user = User.query.filter_by(username=username).first_or_404()
	followers = user.followers.all()
	followers_count = user.followers.count()
	followed = user.followed.all()
	followed_count = user.followed.count()
	now = datetime.utcnow

	if current_user.is_authenticated and user == current_user:
		form = AddRecordForm()
		edit_form = EditRecordForm()

		if form.validate_on_submit():
			# Form data
			artist = form.artist.data
			title = form.title.data
			format_id = 1
			color = form.color.data
			size_id = form.size.data
			year = form.year.data
			notes = form.notes.data
			mail = 1 if form.incoming.data else 0
			add_image_url = form.add_image_url.data

			a = Artist.query.filter_by(name=artist).first()
			if a is None:
				Artist(name=form.artist.data).add_to_table()
				artist_id = Artist.query.filter_by(name=artist).first().id
			else:
				artist_id = a.id

			# See if you already have this title
			t = Title.query.filter_by(
				name=title, artist_id=artist_id, year=year,
				format_id=format_id, size_id=size_id, color=color,
				notes=notes, owner_id=current_user.id).first()

			if t is None:
				Title(
					name=title, artist_id=artist_id, year=year,
					format_id=format_id, size_id=size_id, color=color,
					notes=notes, owner_id=current_user.id, mail=mail).add_to_table()
				record_id = Title.query.filter_by(name=title, artist_id=artist_id, year=year,
					format_id=format_id, size_id=size_id, color=color,
					notes=notes, owner_id=current_user.id, mail=mail).first().id
				if add_image_url:
					image = Image(record_id=record_id, image_url=add_image_url)
					image.add_to_table()
			else:
				flash('You already own this', 'error')
				flash(request.form)
				return redirect(url_for('.user', username=current_user.username))

			flash('{} - {} added'.format(artist, title), 'success')
			return redirect(url_for('.user', username=current_user.username))

		elif request.form.get('edit_id') and edit_form.validate_on_submit():

			# decoded_id = decode_id(str(hashed_id))
			# record = Title.query.filter_by(id=decoded_id).first_or_404()

			record_id = decode_id(str(edit_form.edit_id.data))

			record = Title.query.filter_by(id=record_id).first_or_404()

			if record:

				artist = edit_form.edit_artist.data
				title = edit_form.edit_title.data
				format_id = 1
				color = edit_form.edit_color.data
				size_id = edit_form.edit_size.data
				year = edit_form.edit_year.data
				notes = edit_form.edit_notes.data
				mail = 1 if edit_form.edit_incoming.data else 0
				image_url = edit_form.image_url.data

				a = Artist.query.filter_by(name=artist).first()
				if a is None:
					Artist(name=edit_form.edit_artist.data).add_to_table()
					artist_id = Artist.query.filter_by(name=artist).first().id
				else:
					artist_id = a.id

				record.artist_id = artist_id
				record.name = title
				record.color = color
				record.size_id = size_id
				record.year = year
				record.notes = notes
				record.mail = mail

				db.session.add(record)
				
				i = Image.query.filter_by(record_id=record.id).first()

				if i is None:
					if image_url:
						image = Image(record_id=record.id, image_url=image_url)
						image.add_to_table()
				else:
					if image_url:
						i.image_url = image_url

				db.session.commit()

				flash('{} - {} Updated!'.format(artist, title), 'success')
				return redirect(url_for('.user', username=current_user.username))		

	else:
		form = None
		edit_form = None

	if user != current_user:
		user_records = Title.query.join(
			Artist, Title.artist_id == Artist.id) \
			.join(Size, Title.size_id == Size.id) \
			.join(Format, Title.format_id == Format.id) \
			.add_columns(Artist.name, Size.name, Format.name, Title.mail) \
			.filter(Title.owner_id == user.id).all()
	else:
		user_records = current_user.owned_records()

	# Sort by artist name, then title year
	user_records = sorted(user_records, key=lambda x: (x[1].lower(), x[0].year))
	images = {x.record_id: x.image_url for x in Image.query.all()}
	flash(request.form)
	return render_template(
		'user.html',
		form=form, edit_form=edit_form, user=user, followers=followers,
		followers_count=followers_count, followed=followed, followed_count=followed_count,
		seven_inches=[record for record in user_records if record[2] == 7 and record[4] == 0],
		ten_inches=[record for record in user_records if record[2] == 10 and record[4] == 0],
		twelve_inches=[record for record in user_records if record[2] == 12 and record[4] == 0],
		seven_inches_mail=[record for record in user_records if record[2] == 7 and record[4] == 1],
		ten_inches_mail=[record for record in user_records if record[2] == 10 and record[4] == 1],
		twelve_inches_mail=[record for record in user_records if record[2] == 12 and record[4] == 1],
		user_records_count=len(user_records),
		encode_id=encode_id, now=now, images=images)


@main.route('/<username>/follower_records', methods=["GET", "POST"])
@login_required
def user_fr(username):

	fr = User.query.filter_by(username=username).first_or_404().follower_records().limit(10).all()

	# Sort by ID descending
	fr.sort(key=lambda x: x[0].id, reverse=True)

	json_records = {}

	for i in range(len(fr)):
		json_records[i] = {
			"artist": fr[i][2],
			"title": fr[i][0].name,
			"user": "you" if fr[i][-1] == username else fr[i][-1],
			"timestamp": fr[i][0].timestamp,
			"gravatar": gravatar(fr[i][1]),
			"id": fr[i][0].id
		}

	return jsonify(json_records)


@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
	form = EditProfileForm()
	if form.validate_on_submit():
		current_user.name = form.name.data
		current_user.location = form.location.data
		current_user.about_me = form.about_me.data
		db.session.add(current_user)
		db.session.commit()
		flash('Your profile has been updated.', 'success')
		return redirect(url_for('.user', username=current_user.username))
	form.name.data = current_user.name
	form.location.data = current_user.location
	form.about_me.data = current_user.about_me

	return render_template('edit_profile.html', form=form, user=current_user)


@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
	user = User.query.get_or_404(id)
	form = EditProfileAdminForm(user=user)
	if form.validate_on_submit():
		user.email = form.email.data
		user.username = form.username.data
		user.confirmed = form.confirmed.data
		user.role = Role.query.get(form.role.data)
		user.name = form.name.data
		user.location = form.location.data
		user.about_me = form.about_me.data
		db.session.add(user)
		db.session.commit()
		flash('Your settings have been updated.', 'success')
		return redirect(url_for('.user', username=user.username))
	form.email.data = user.email
	form.username.data = user.username
	form.confirmed.data = user.confirmed
	form.role.data = user.role_id
	form.name.data = user.name
	form.location.data = user.location
	form.about_me.data = user.about_me

	return render_template('admin_edit_profile.html', form=form, user=user)


@main.route('/follow/<username>')
@login_required
def follow(username):
	user = User.query.filter_by(username=username).first()
	if user is None:
		flash('Invalid user.', 'error')
		return redirect(url_for('.index'))
	if current_user.is_following(user):
		flash('You are already following this user.', '')
		return redirect(url_for('.user', username=username))
	current_user.follow(user)
	send_email(
		user.email,
		'{} is now following you'.format(current_user.username),
		'auth/email/followed_by', user=user, current_user=current_user)
	flash('You are now following {}.'.format(username), 'success')
	return redirect(url_for('.user', username=username))


@main.route('/unfollow/<username>')
@login_required
def unfollow(username):
	user = User.query.filter_by(username=username).first()
	if user is None:
		flash('Invalid user.', 'error')
		return redirect(url_for('.index'))
	if not current_user.is_following(user):
		flash('You are not following this user.', 'error')
		return redirect(url_for('.user', username=username))
	current_user.unfollow(user)
	flash('You are not following {} anymore.'.format(username), 'success')
	return redirect(url_for('.user', username=username))


@main.route('/delete-record/<hashed_id>')
@login_required
def delete_record(hashed_id):
	decoded_id = decode_id(str(hashed_id))
	record = Title.query.filter_by(id=decoded_id).first_or_404()
	image = Image.query.filter_by(record_id=record.id).first()

	if record.owner_id == current_user.id:
		artist = Artist.query.filter_by(id=record.artist_id).first().name
		title = record.name
		if image:
			image.delete_from_table()
		record.delete_from_table()
		
		flash("{} - {} Deleted!".format(artist, title), 'success')
		return redirect(url_for('.user', username=current_user.username))
	else:
		flash("You dont own that", 'error')
		return redirect(url_for('.user', username=current_user.username))


@main.route('/download/<username>')
@login_required
def download(username):
	import StringIO
	import csv
	user = User.query.filter_by(username=username).first()
	if user == current_user:

		head_column = ["Artist", "Title", "Color", "Year", "Size", "Date Added"]

		si = StringIO.StringIO()
		cw = csv.writer(si)
		cw.writerow(head_column)

		sorted_list = sorted(user.owned_records(), key=lambda x: (x[2], x[0].year, x[1], x[0].name))
		for row in sorted_list:
			title, artist, size, format, mail = row
			cw.writerow([
				artist, title.name,
				title.color, title.year,
				size, title.timestamp.strftime('%m/%d/%y')])

		output = make_response(si.getvalue())
		now = datetime.now().strftime('%m/%d/%y')
		output.headers["Content-Disposition"] = "attachment; filename={}_records_{}.csv".format(username, now)
		output.headers["Content-type"] = "text/csv"
		return output
	else:
		return redirect(url_for('main.index'))
