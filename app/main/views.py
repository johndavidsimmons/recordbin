from flask import render_template, session, redirect, url_for, current_app, abort, flash, request, jsonify
from flask_login import login_required, current_user
from .. import db
from ..models import User, Role	, AnonymousUser, Permission, Artist, Title, Size, Format, Follow, gravatar, user_local_time
from . import main
from .forms import EditProfileForm, EditProfileAdminForm, AddRecordForm
from ..decorators import admin_required, permission_required
from werkzeug.local import LocalProxy
from datetime import datetime

@main.route('/users', methods=['GET', 'POST'])
def all_users():
	all_users = User.query.all()
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
		follower_records = current_user.follower_records()

	else:
		follower_records = None

	return render_template('index.html', db=db, follower_records=follower_records, gravatar=gravatar, now = user_local_time(datetime.utcnow))
	


@main.route('/<username>', methods=["GET", "POST"])
def user(username):
	user = User.query.filter_by(username=username).first_or_404()
	followers = user.followers.all()
	followers_count = user.followers.count()
	followed = user.followed.all()
	followed_count = user.followed.count()

	if current_user.is_authenticated and user == current_user:
		form = AddRecordForm()

		if form.validate_on_submit():

			# Form data
			artist = form.artist.data
			title = form.title.data
			format_id = form.format.data
			color = form.color.data
			size_id = form.size.data
			year = form.year.data
			notes = form.notes.data

			
				
			a = Artist.query.filter_by(name=artist).first()
			if a is None:
				Artist(name=form.artist.data).add_to_table()
				artist_id = Artist.query.filter_by(name=artist).first().id
			else:
				artist_id = a.id

			# See if you already have this
			t = Title.query.filter_by(name=title, artist_id=artist_id, year=year, format_id=format_id, size_id=size_id, color=color, notes=notes, owner_id=current_user.id).first()
					
			if t is None:
				Title(name=title, artist_id=artist_id, year=year, format_id=format_id, size_id=size_id, color=color, notes=notes, owner_id=current_user.id).add_to_table()
			else:
				flash('You already own this')
				return redirect(url_for('.user', username=current_user.username))
				

			flash('{} - {} added'.format(artist, title))
			return redirect(url_for('.user', username=current_user.username))

	else:
		form = None

	if user != current_user:
		user_records = Title.query.join(Artist, Title.artist_id==Artist.id).join(Size, Title.size_id==Size.id).join(Format, Title.format_id==Format.id).add_columns(Artist.name, Size.name, Format.name).filter(Title.owner_id==user.id).all()
	else:
		user_records = current_user.owned_records()

	# Sort by artist name, then title year
	user_records = sorted(user_records, key=lambda x: (x[1].lower(), x[0].year))



	return render_template('user.html', 
		form=form, user=user, followers=followers, 
		followers_count = followers_count, followed=followed, followed_count=followed_count, 
		seven_inches=[record for record in user_records if record[2] == 7],
		ten_inches=[record for record in user_records if record[2] == 10],
		twelve_inches=[record for record in user_records if record[2] == 12],
		user_records_count=len(user_records))

@main.route('/<username>/follower_records', methods=["GET", "POST"])
@login_required
def user_fr(username):

	fr = User.query.filter_by(username=username).first_or_404().follower_records().limit(10).all()

	# Sort by ID descending
	fr.sort(key=lambda x: x[0].id, reverse=True)

	json_records = {
		
	}

	for i in range(len(fr)):
		json_records[i] = { 
			"artist" : fr[i][2], 
			"title" : fr[i][0].name, 
			"user" : "you" if fr[i][-1] == username else fr[i][-1], 
			"timestamp": fr[i][0].timestamp, 
			"gravatar" : gravatar(fr[i][1]), 
			"id" : fr[i][0].id 
		}

	return  jsonify(json_records)

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
		flash('Your profile has been updated.')
		return redirect(url_for('.user', username=current_user.username))
	form.name.data = current_user.name
	form.location.data = current_user.location
	form.about_me.data = current_user.about_me
	return render_template('edit_profile.html', form=form)


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
		flash('The profile has been updated.')
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
		flash('Invalid user.')
		return redirect(url_for('.index'))
	if current_user.is_following(user):
		flash('You are already following this user.')
		return redirect(url_for('.user', username=username))
	current_user.follow(user)
	flash('You are now following %s.' % username)
	return redirect(url_for('.user', username=username))


@main.route('/unfollow/<username>')
@login_required
def unfollow(username):
	user = User.query.filter_by(username=username).first()
	if user is None:
		flash('Invalid user.')
		return redirect(url_for('.index'))
	if not current_user.is_following(user):
		flash('You are not following this user.')
		return redirect(url_for('.user', username=username))
	current_user.unfollow(user)
	flash('You are not following %s anymore.' % username)
	return redirect(url_for('.user', username=username))

@main.route('/delete-record/<id>')
@login_required
def delete_record(id):
	record = Title.query.filter_by(id=id).first_or_404()
	record.delete_from_table()
	flash("DELETED")
	return redirect(url_for('.user', username=current_user.username))
