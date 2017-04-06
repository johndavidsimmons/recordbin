import unittest
from app import create_app, db
from app.models import User, Role, Size, Format, Title
from flask import url_for


class FlaskClientTestCase(unittest.TestCase):
	def setUp(self):
		self.app = create_app('testing')
		self.app.secret_key = "testing"
		self.app.config['WTF_CSRF_ENABLED'] = False
		self.app_context = self.app.app_context()
		self.app_context.push()
		db.create_all()
		Role.insert_roles()
		Format.insert_formats()
		Size.insert_sizes()
		self.client = self.app.test_client(use_cookies=True)

		user_role = Role.query.filter_by(name='user').first()
		admin_role = Role.query.filter_by(name='admin').first()
		user = User(
			email='profile_john@example.com',
			username='profile_john',
			password='yolo',
			about_me="Overlord",
			role=admin_role,
			confirmed=True)
		db.session.add(user)
		user2 = User(
			email='profile_john2@example.com',
			username='profile_john2',
			password='yolo',
			about_me="not in charge",
			role=user_role,
			confirmed=True)
		db.session.add(user2)
		db.session.commit()

	def tearDown(self):
		db.session.remove()
		db.drop_all()
		self.app_context.pop()

	def login(self, email, password):
		return self.client.post(url_for("auth.login"), data=dict(
			email=email, password=password, remember_me=True),
			follow_redirects=True)

	def logout(self):
		return self.client.get(url_for("auth.logout"), follow_redirects=True)

	def register(self, email, username, password, password2):
		return self.client.post(url_for("auth.register"), data=dict(
			email=email, password=password, username=username, password2=password), follow_redirects=True)

	def add_record(self, username):
		return self.client.post(
			url_for("main.user", username=username),
			data=dict(
				artist="Black Sabbath",
				title="Master of Reality",
				format=1,
				color="Black",
				size=3,
				year=1970,
				notes="Lorem"),
			follow_redirects=True)

	def delete_record(self, record_id):
		return self.client.get(url_for('main.delete_record', id=record_id), follow_redirects=True)

	def edit_profile(self):
		return self.client.post(
			url_for("main.edit_profile"),
			data=dict(about_me="This is new"), follow_redirects=True)

	# Functionality
	def test_login_and_logout(self):
		response = self.login(email="profile_john@example.com", password="yolo")
		assert "Hello, profile_john@example.com!" in response.data
		response = self.logout()
		assert "You have logged out" in response.data

	def test_nonexistent_user(self):
		response = self.login(email="fakeuser@example.com", password="yolo")
		assert "invalid username or password" in response.data

	def test_invalid_email_format(self):
		response = self.login(email="fakeuser", password="yolo")
		assert "Invalid email address" in response.data

	def test_email_and_password_required(self):
		response = self.login(email="", password="")
		assert "Email is required" in response.data
		assert "Password is required" in response.data

	def test_invalid_password(self):
		response = self.login(email="profile_john@example.com", password="yolo1")
		assert "invalid username or password" in response.data

	def test_add_record(self):
		# Login
		self.login(email="profile_john@example.com", password="yolo")
		response = self.add_record(username="profile_john")
		assert "Black Sabbath - Master of Reality added" in response.data

	def test_delete_record(self):
		self.login(email="profile_john@example.com", password="yolo")
		self.add_record(username="profile_john")
		response = self.delete_record(Title.query.first().id)
		assert "DELETED" in response.data

	def test_delete_nonowned_record(self):
		self.login(email="profile_john@example.com", password="yolo")
		self.add_record(username="profile_john")
		self.logout()
		self.login(email="profile_john2@example.com", password="yolo")
		response = self.delete_record(Title.query.first().id)
		assert "You dont own that" in response.data

	def test_edit_profile(self):
		self.login(email="profile_john@example.com", password="yolo")
		response = self.client.get("/edit-profile")
		assert "Overlord" in response.data
		response = self.edit_profile()
		assert "This is new" in response.data

	def test_admin_edit_profile(self):
		self.login(email="profile_john@example.com", password="yolo")
		response = self.client.get("/edit-profile/1")
		assert "Confirmed" in response.data
		assert "Overlord" in response.data
		response = self.edit_profile()
		assert "This is new" in response.data

	def test_admin_edit_other_profile(self):
		self.login(email="profile_john@example.com", password="yolo")
		response = self.client.get("/edit-profile/2")
		assert "Confirmed" in response.data
		assert "not in charge" in response.data
		response = self.edit_profile()
		assert "This is new" in response.data

	def test_user_edit_other_profile(self):
		self.login(email="profile_john2@example.com", password="yolo")
		response = self.client.get("/edit-profile/1")
		assert response.status_code == 403

	def test_register(self):
		response = self.client.get(url_for("auth.register"))
		assert "Register" in response.data
		response = self.register(
			email="test@example.com", username="test", password="test", password2="test")
		assert "A confirmation email has been sent to you by email." in response.data

		response = self.login(email="test@example.com", password="test")
		assert "Need another confirmation email?" in response.data

		test_user = User.query.filter_by(email="test@example.com").first()
		test_user.confirmed = True

		response = self.client.get(url_for("main.index"))
		assert "Hello, test@example.com" in response.data

	def test_register_email_exists(self):
		response = self.client.get(url_for("auth.register"))
		assert "Register" in response.data
		response = self.register(
			email="profile_john@example.com", username="test", password="test", password2="test")
		assert "Email already registered." in response.data

	def test_register_username_exists(self):
		response = self.client.get(url_for("auth.register"))
		assert "Register" in response.data
		response = self.register(
			email="yolo@example.com", username="profile_john", password="test", password2="test")
		assert "Username already registered." in response.data

	# Status Code
	def test_home_page_status(self):
		response = self.client.get(url_for('main.index'))
		assert response.status_code == 200

	def test_login_page_status(self):
		response = self.client.get(url_for('auth.login'))
		assert response.status_code == 200

	def test_register_page_status(self):
		response = self.client.get(url_for('auth.register'))
		assert response.status_code == 200

	def test_password_reset_page_status(self):
		response = self.client.get(url_for('auth.password_reset_request'))
		assert response.status_code == 200

	def test_public_profile_page_status(self):
		response = self.client.get('/profile_john')
		assert response.status_code == 200

	def test_all_users_page_status(self):
		response = self.client.get(url_for('main.all_users'))
		assert response.status_code == 200

	def test_404_status(self):
		response = self.client.get("/yolo")
		assert response.status_code == 404

	def test_unconfirmed_redirect(self):
		response = self.client.get(url_for('auth.unconfirmed'))
		assert response.status_code == 302

	def test_change_email_redirect(self):
		response = self.client.get(url_for('auth.change_email_request'))
		assert response.status_code == 302

	def test_change_password_redirect(self):
		response = self.client.get(url_for('auth.change_password'))
		assert response.status_code == 302

	def test_logout_redirect(self):
		response = self.client.get(url_for('auth.logout'))
		assert response.status_code == 302

	def test_confirm_resend_redirect(self):
		response = self.client.get(url_for('auth.resend_confirmation'))
		assert response.status_code == 302

	def test_confirm_redirect(self):
		response = self.client.get(url_for('auth.confirm', token='xyz'))
		assert response.status_code == 302

	def test_edit_profile_redirect(self):
		response = self.client.get("/edit-profile")
		assert response.status_code == 302

	def test_admin_edit_profile_redirect(self):
		response = self.client.get("/edit-profile/1")
		assert response.status_code == 302
