import unittest
from app import create_app, db
from app.models import User, Role
from flask import url_for

class FlaskClientTestCase(unittest.TestCase):
	def setUp(self):
		self.app = create_app('testing')
		self.app.secret_key = "testing"
		self.app_context = self.app.app_context()
		self.app_context.push()
		db.create_all()
		Role.insert_roles()
		self.client = self.app.test_client(use_cookies=True)

		user_role = Role.query.filter_by(name='user').first()
		user = User(email='profile_john@example.com',
					username='profile_john', password='yolo',
					role=user_role, confirmed=True)
		db.session.add(user)
		db.session.commit()

	def tearDown(self):
		db.session.remove()
		db.drop_all()
		self.app_context.pop()

	# 200
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

	# 404
	def test_404_status(self):
		response = self.client.get("/yolo")
		assert response.status_code == 404

	#302 
	# Anonymous Users
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