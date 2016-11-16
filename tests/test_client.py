import unittest
from app import create_app, db
from app.models import User, Role
from flask import url_for

class FlaskClientTestCase(unittest.TestCase):
	def setUp(self):
		self.app = create_app('testing')
		self.app_context = self.app.app_context()
		self.app_context.push()
		db.create_all()
		Role.insert_roles()
		self.client = self.app.test_client(use_cookies=True)

	def tearDown(self):
		db.session.remove()
		db.drop_all()
		self.app_context.pop()

	def test_home_page(self):
		response = self.client.get(url_for('main.index'))
		self.assertTrue('Stranger' in response.get_data(as_text=True))
		self.assertTrue(response.status_code == 200)

	def test_login_page(self):
		response = self.client.get(url_for('auth.login'))
		self.assertTrue('Login' in response.get_data(as_text=True))
		self.assertTrue(response.status_code == 200)	

	def test_register_page(self):
		response = self.client.get(url_for('auth.register'))
		self.assertTrue('Register' in response.get_data(as_text=True))
		self.assertTrue(response.status_code == 200)		

	def test_password_reset_page(self):
		response = self.client.get(url_for('auth.password_reset_request'))
		self.assertTrue('Reset' in response.get_data(as_text=True))
		self.assertTrue(response.status_code == 200)

	def test_404(self):
		response = self.client.get('/yolo')
		self.assertTrue(response.status_code == 404)

	# Redirects
	def test_unconfirmed_redirect(self):
		response = self.client.get(url_for('auth.unconfirmed'))
		self.assertTrue(response.status_code == 302)