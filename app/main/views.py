from flask import render_template, session, redirect, url_for, current_app, abort, flash, request
from flask_login import login_required, current_user
from .. import db
from ..models import User, Role	, AnonymousUser, Permission, Artist, Title, Size, Format
from . import main
from .forms import EditProfileForm, EditProfileAdminForm, AddRecordForm
from ..decorators import admin_required, permission_required

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
	form = AddRecordForm()
	records = Title.query.join(Artist, Title.artist_id==Artist.id).join(Format, Title.format_id==Format.id).join(Size, Title.size_id==Size.id).add_columns(Artist.name, Format.name, Size.name).filter(Title.artist_id==Artist.id).all()

	if form.validate_on_submit():

		# Form data
		artist = form.artist.data
		title = form.title.data
		format_id = form.format.data
		color = form.color.data
		size_id = form.size.data
		
		# Check if artist in artists table
		# If not, add it, then get id
		try:
			artist_id = Artist.query.filter_by(name=artist).first().id
		except AttributeError:
			Artist(name=form.artist.data).add_to_table()
			artist_id = Artist.query.filter_by(name=artist).first().id

		# Build object and add to collection
		record = Title(name=title, artist_id=artist_id, year=2012, format_id=format_id, size_id=size_id, color=color, notes="lorem ipsum")
		
		record.add_to_collection()

		flash('{} - {} added'.format(artist, title))
		return redirect(url_for('main.index'))

	return render_template('index.html', db=db, records=records, form=form)

@main.route('/dataview')
def dataview():
	records = Record.query.all()
	return render_template('dataview.html', records = records)


@main.route('/user/<username>')
def user(username):
	user = User.query.filter_by(username=username).first_or_404()
	followers = user.followers.all()
	followers_count = user.followers.count()
	followed = user.followed.all()
	followed_count = user.followed.count()
	return render_template('user.html', user=user, followers=followers, followers_count = followers_count, followed=followed, followed_count=followed_count)


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