import re
import threading
import time
import unittest
from selenium import webdriver
from app import create_app, db
from app.models import Role, User


class SeleniumTestCase(unittest.TestCase):
	client = None
	
	@classmethod
	def setUpClass(cls):
		# start Firefox
		try:
			cls.client = webdriver.Chrome('/Users/jsimmons/recordbin/venv/selenium/webdriver/chrome/chromedriver')
		except:
			pass

		# skip these tests if the browser could not be started
		if cls.client:
			# create the application
			cls.app = create_app('testing')
			cls.app_context = cls.app.app_context()
			cls.app_context.push()

			# suppress logging to keep unittest output clean
			import logging
			logger = logging.getLogger('werkzeug')
			logger.setLevel("ERROR")

			# create the database and populate with some fake data
			db.create_all()
			Role.insert_roles()
			# User.generate_fake(10)
			# Post.generate_fake(10)

			# add an administrator user
			admin_role = Role.query.filter_by(name='admin').first()
			admin = User(email='admin_john@example.com',
						 username='admin_john', password='yolo',
						 role=admin_role, confirmed=True)
			db.session.add(admin)

			# add a regular user
			user_role = Role.query.filter_by(name='user').first()
			user = User(email='user_john@example.com',
						username='user_john', password='yolo',
						role=user_role, confirmed=True)
			db.session.add(user)

			# add an unconfirmed user
			unconfirmed_user = User(email='unconfirmed_john@example.com',
							username='unconfirmed_john', password='yolo',
							role=user_role, confirmed=False)
			db.session.add(unconfirmed_user)

			# add a change password user
			change_password_user = User(email='change_password_john@example.com', username='change_password_john', password='yolo', role=user_role, confirmed=False)
			db.session.add(change_password_user)

			# add a change email user
			change_email_user = User(email='change_email_john@example.com',
			username='change_email_john', password='yolo', role=user_role,confirmed=True)
			db.session.add(change_email_user)

			# Commit the users
			db.session.commit()

			# start the Flask server in a thread
			threading.Thread(target=cls.app.run).start()

			# give the server a second to ensure it is up
			time.sleep(1) 

	@classmethod
	def tearDownClass(cls):
		if cls.client:
			# stop the flask server and the browser
			cls.client.get('http://localhost:5000/shutdown')
			cls.client.close()

			# destroy database
			db.drop_all()
			db.session.remove()

			# remove application context
			cls.app_context.pop()

	def setUp(self):
		if not self.client:
			self.skipTest('Web browser not available')

	def tearDown(self):
		pass
	
	def test_admin_home_page(self):
		# navigate to home page
		self.client.get('http://localhost:5000/')
		self.assertTrue(re.search('Hello, Stranger!', self.client.page_source))

		# navigate to login page
		self.client.find_element_by_link_text('Log In').click()
		self.assertTrue('<h1>Login</h1>' in self.client.page_source)

		# login
		self.client.find_element_by_name('email').\
			send_keys('admin_john@example.com')
		self.client.find_element_by_name('password').send_keys('yolo')
		self.client.find_element_by_name('submit').click()
		self.assertTrue(re.search('Hello, admin_john@example.com!', self.client.page_source))

		# logout
		self.client.find_element_by_link_text('Log Out').click()
		self.assertTrue(re.search('Hello, Stranger!', self.client.page_source))

	def test_admin_profile_view(self):
		# navigate to home page
		self.client.get('http://localhost:5000/')
		self.assertTrue(re.search('Hello, Stranger!', self.client.page_source))

		# navigate to login page
		self.client.find_element_by_link_text('Log In').click()
		self.assertTrue('<h1>Login</h1>' in self.client.page_source)

		# login
		self.client.find_element_by_name('email').\
			send_keys('admin_john@example.com')
		self.client.find_element_by_name('password').send_keys('yolo')
		self.client.find_element_by_name('submit').click()
		self.assertTrue(re.search('Hello, admin_john@example.com!', self.client.page_source))

		# navigate to the user's profile page
		self.client.find_element_by_link_text('View Profile').click()
		self.assertTrue('<p><strong>username:</strong> admin_john</p>' in self.client.page_source)

		# logout
		self.client.find_element_by_link_text('Log Out').click()
		time.sleep(1)
		self.assertTrue(re.search('Hello, Stranger!', self.client.page_source))

	def test_admin_profile_edit(self):
		# navigate to home page
		self.client.get('http://localhost:5000/')
		self.assertTrue(re.search('Hello, Stranger!', self.client.page_source))

		# navigate to login page
		self.client.find_element_by_link_text('Log In').click()
		self.assertTrue('<h1>Login</h1>' in self.client.page_source)

		# login
		self.client.find_element_by_name('email').\
			send_keys('admin_john@example.com')
		self.client.find_element_by_name('password').send_keys('yolo')
		self.client.find_element_by_name('submit').click()
		self.assertTrue(re.search('Hello, admin_john@example.com!', self.client.page_source))

		# navigate to the user's profile page
		self.client.find_element_by_link_text('View Profile').click()
		self.assertTrue('<p><strong>username:</strong> admin_john</p>' in self.client.page_source)

		# navigate to the edit profile page
		self.client.find_element_by_link_text('Edit Profile [Admin]').click()
		self.assertTrue('<h1>Edit Profile</h1>' in self.client.page_source)

		# Fill out profile and save
		self.client.find_element_by_name('about_me').send_keys('Lorem ipsum dolor sit amet, consectetur adipisicing elit. Eos iste animi, ratione distinctio non, dolorum asperiores nam aliquam architecto quidem quibusdam est doloribus harum blanditiis voluptas tempora ducimus ipsam repudiandae!')
		self.client.find_element_by_name('submit').click()
		self.assertTrue(re.search('Lorem ipsum dolor sit amet, consectetur adipisicing elit. Eos iste animi, ratione distinctio non, dolorum asperiores nam aliquam architecto quidem quibusdam est doloribus harum blanditiis voluptas tempora ducimus ipsam repudiandae!', self.client.page_source))

		# logout
		self.client.find_element_by_link_text('Log Out').click()
		self.assertTrue(re.search('Hello, Stranger!', self.client.page_source))

	def test_user_profile_view(self):
		# navigate to home page
		self.client.get('http://localhost:5000/')
		self.assertTrue(re.search('Hello, Stranger!', self.client.page_source))

		# navigate to login page
		self.client.find_element_by_link_text('Log In').click()
		self.assertTrue('<h1>Login</h1>' in self.client.page_source)

		# login
		self.client.find_element_by_name('email').\
			send_keys('user_john@example.com')
		self.client.find_element_by_name('password').send_keys('yolo')
		self.client.find_element_by_name('submit').click()
		self.assertTrue(re.search('Hello, user_john@example.com!', self.client.page_source))

		# navigate to the user's profile page
		self.client.find_element_by_link_text('View Profile').click()
		self.assertTrue('<p><strong>username:</strong> user_john</p>' in self.client.page_source)

		# logout
		self.client.find_element_by_link_text('Log Out').click()
		self.assertTrue(re.search('Hello, Stranger!', self.client.page_source))

	def test_user_profile_edit(self):

		email = User.query.filter_by(username="user_john").first().email
		username = User.query.filter_by(email="user_john@example.com").first().username

		# navigate to home page
		self.client.get('http://localhost:5000/')
		self.assertTrue(re.search('Hello, Stranger!', self.client.page_source))

		# navigate to login page
		self.client.find_element_by_link_text('Log In').click()
		self.assertTrue('<h1>Login</h1>' in self.client.page_source)

		# login
		self.client.find_element_by_name('email').\
			send_keys(email)
		self.client.find_element_by_name('password').send_keys('yolo')
		self.client.find_element_by_name('submit').click()
		self.assertTrue(re.search('Hello, {email}!'.format(email=email), self.client.page_source))

		# navigate to the user's profile page
		self.client.find_element_by_link_text('View Profile').click()
		self.assertTrue('<p><strong>username:</strong> {username}</p>'.format(username=username) in self.client.page_source)

		# navigate to the edit profile page
		self.client.find_element_by_link_text('Edit Profile').click()
		self.assertTrue('<h1>Edit Profile</h1>' in self.client.page_source)

		# Fill out profile and save
		self.client.find_element_by_name('about_me').send_keys('Lorem ipsum dolor sit amet, consectetur adipisicing elit. Eos iste animi, ratione distinctio non, dolorum asperiores nam aliquam architecto quidem quibusdam est doloribus harum blanditiis voluptas tempora ducimus ipsam repudiandae!')
		self.client.find_element_by_name('submit').click()
		self.assertTrue(re.search('Lorem ipsum dolor sit amet, consectetur adipisicing elit. Eos iste animi, ratione distinctio non, dolorum asperiores nam aliquam architecto quidem quibusdam est doloribus harum blanditiis voluptas tempora ducimus ipsam repudiandae!', self.client.page_source))

		# logout
		self.client.find_element_by_link_text('Log Out').click()
		self.assertTrue(re.search('Hello, Stranger!', self.client.page_source))
	 
	def test_user_unconfirmed(self):

		email = User.query.filter_by(username='unconfirmed_john').first().email

		# navigate to home page
		self.client.get('http://localhost:5000/')
		self.assertTrue(re.search('Hello, Stranger!', self.client.page_source))

		# navigate to login page
		self.client.find_element_by_link_text('Log In').click()
		self.assertTrue('<h1>Login</h1>' in self.client.page_source)

		# login
		self.client.find_element_by_name('email').send_keys(email)
		self.client.find_element_by_name('password').send_keys('yolo')
		self.client.find_element_by_name('submit').click()
		self.assertTrue(re.search('You have not confirmed your account yet.', self.client.page_source))

		# logout
		self.client.find_element_by_link_text('Log Out').click()
		self.assertTrue(re.search('Hello, Stranger!', self.client.page_source))

	def test_change_password(self):

		email = User.query.filter_by(username='change_password_john').first().email
		password = 'yolo'
		new_password = 'yolo1'

		# navigate to home page
		self.client.get('http://localhost:5000/')
		self.assertTrue(re.search('Hello, Stranger!', self.client.page_source))

		# navigate to login page
		self.client.find_element_by_link_text('Log In').click()
		self.assertTrue('<h1>Login</h1>' in self.client.page_source)

		# login
		self.client.find_element_by_name('email').\
			send_keys(email)
		self.client.find_element_by_name('password').send_keys(password)
		self.client.find_element_by_name('submit').click()
		self.assertTrue(re.search('Hello, {email}!'.format(email=email), self.client.page_source))

		# navigate to the change password page
		self.client.find_element_by_link_text('Change Password').click()
		self.assertTrue(re.search('Change password', self.client.page_source))
		self.client.find_element_by_name('old_password').send_keys(password)
		self.client.find_element_by_name('password').send_keys(new_password)
		self.client.find_element_by_name('password2').send_keys(new_password)
		self.client.find_element_by_name('submit').click()
		self.assertTrue(re.search('Your password has been updated.', self.client.page_source))

		# logout
		self.client.find_element_by_link_text('Log Out').click()
		self.assertTrue(re.search('Hello, Stranger!', self.client.page_source))

		# navigate to login page
		self.client.find_element_by_link_text('Log In').click()
		self.assertTrue('<h1>Login</h1>' in self.client.page_source)

		# login
		self.client.find_element_by_name('email').send_keys(email)
		self.client.find_element_by_name('password').send_keys('yolo1')
		self.client.find_element_by_name('submit').click()
		self.assertTrue(re.search('Hello, {email}!'.format(email=email), self.client.page_source))

		# logout
		self.client.find_element_by_link_text('Log Out').click()
		self.assertTrue(re.search('Hello, Stranger!', self.client.page_source))

	def test_change_email(self):
		email = User.query.filter_by(username='change_email_john').first().email
		new_email = 'change_email_john2@example.com'
		password = 'yolo'


		# navigate to home page
		self.client.get('http://localhost:5000/')
		self.assertTrue(re.search('Hello, Stranger!', self.client.page_source))

		# navigate to login page
		self.client.find_element_by_link_text('Log In').click()
		self.assertTrue('<h1>Login</h1>' in self.client.page_source)

		# login
		self.client.find_element_by_name('email').send_keys(email)
		self.client.find_element_by_name('password').send_keys(password)
		self.client.find_element_by_name('submit').click()
		self.assertTrue(re.search('Hello, {email}!'.format(email=email), self.client.page_source))	

		# navigate to change email page
		self.client.find_element_by_link_text('Change Email').click()
		self.client.find_element_by_name('email').send_keys(new_email)
		self.client.find_element_by_name('password').send_keys(password)
		token = User.query.filter_by(username='change_email_john').first().generate_email_change_token(new_email)
		
		# Navigate to the change token page
		self.client.get('http://localhost:5000/auth/change-email/{token}'.format(token=token))
		self.assertTrue(re.search('Hello, {new_email}!'.format(new_email=new_email), self.client.page_source))

		# logout
		self.client.find_element_by_link_text('Log Out').click()
		self.assertTrue(re.search('Hello, Stranger!', self.client.page_source))

	def test_active_navigation_selectors(self):

		# navigate to home page
		self.client.get('http://localhost:5000/')
		self.assertTrue('''<a class="active" href="/">Home</a>''' in self.client.page_source)

		# navigate to login
		self.client.get('http://localhost:5000/auth/login')
		self.assertTrue('<a class="active" href="/auth/login">Log In</a>' in self.client.page_source)

		# navigate to register
		self.client.get('http://localhost:5000/auth/register')
		self.assertTrue('<a class="active" href="/auth/register">Register</a>' in self.client.page_source)
	
	def test_login_redirect(self):
		"""
		A logged in user trying to access the login page
		will be redirected to the index page
		"""	

		# navigate to home page
		self.client.get('http://localhost:5000/')
		self.assertTrue(re.search('Hello, Stranger!', self.client.page_source))

		# navigate to login page
		self.client.find_element_by_link_text('Log In').click()
		self.assertTrue('<h1>Login</h1>' in self.client.page_source)

		# login
		self.client.find_element_by_name('email').\
			send_keys('admin_john@example.com')
		self.client.find_element_by_name('password').send_keys('yolo')
		self.client.find_element_by_name('submit').click()
		self.assertTrue(re.search('Hello, admin_john@example.com!', self.client.page_source))

		self.client.get('http://localhost:5000/auth/login')
		self.assertTrue(re.search('Hello, admin_john@example.com!', self.client.page_source))

		# logout
		self.client.find_element_by_link_text('Log Out').click()
		self.assertTrue(re.search('Hello, Stranger!', self.client.page_source))

	def test_register_redirect(self):
		"""
		A logged in user trying to access the register page
		will be redirected to the index page
		"""	

		# navigate to home page
		self.client.get('http://localhost:5000/')
		self.assertTrue(re.search('Hello, Stranger!', self.client.page_source))

		# navigate to login page
		self.client.find_element_by_link_text('Log In').click()
		self.assertTrue('<h1>Login</h1>' in self.client.page_source)

		# login
		self.client.find_element_by_name('email').\
			send_keys('admin_john@example.com')
		self.client.find_element_by_name('password').send_keys('yolo')
		self.client.find_element_by_name('submit').click()
		self.assertTrue(re.search('Hello, admin_john@example.com!', self.client.page_source))

		self.client.get('http://localhost:5000/auth/register')
		self.assertTrue(re.search('Hello, admin_john@example.com!', self.client.page_source))

		# logout
		self.client.find_element_by_link_text('Log Out').click()
		self.assertTrue(re.search('Hello, Stranger!', self.client.page_source))	