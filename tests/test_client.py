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

	# def test_login_page(self):
	# 	response = self.client.get(url_for('auth.login'))
	# 	self.assertTrue('Login' in response.get_data(as_text=True))
	# 	self.assertTrue(response.status_code == 200)	

	# def test_register_page(self):
	# 	response = self.client.get(url_for('auth.register'))
	# 	self.assertTrue('Register' in response.get_data(as_text=True))
	# 	self.assertTrue(response.status_code == 200)		

	# def test_password_reset_page(self):
	# 	response = self.client.get(url_for('auth.password_reset_request'))
	# 	self.assertTrue('Reset' in response.get_data(as_text=True))
	# 	self.assertTrue(response.status_code == 200)

	# def test_404(self):
	# 	response = self.client.get('/yolo')
	# 	self.assertTrue(response.status_code == 404)

	# def test_public_profile_page(self):
	# 	response = self.client.get('/profile_john')
	# 	self.assertTrue(response.status_code == 200)

	# Redirects for anon users
	# def test_unconfirmed_redirect(self):
	# 	response = self.client.get(url_for('auth.unconfirmed'))
	# 	self.assertTrue(response.status_code == 302)

	# def test_admin_settings_redirect(self):
	# 	response = self.client.get(url_for('auth.admin_settings'))
	# 	self.assertTrue(response.status_code == 302)

	# def test_change_email_redirect(self):
	# 	response = self.client.get(url_for('auth.change_email_request'))
	# 	self.assertTrue(response.status_code == 302)

	# def test_change_password_redirect(self):
	# 	response = self.client.get(url_for('auth.change_password'))
	# 	self.assertTrue(response.status_code == 302)

	# def test_logout_redirect(self):
	# 	response = self.client.get(url_for('auth.logout'))
	# 	self.assertTrue(response.status_code == 302)

	# def test_confirm_resend_redirect(self):
	# 	response = self.client.get(url_for('auth.resend_confirmation'))
	# 	self.assertTrue(response.status_code == 302)

	# def test_confirm_redirect(self):
	# 	response = self.client.get(url_for('auth.confirm', token='xyz'))
	# 	self.assertTrue(response.status_code == 302)			