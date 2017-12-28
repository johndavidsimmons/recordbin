import time

from flask import url_for
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from app import db
from app.models import Role, User
from tests.client.base import screenshot_exceptions, SeleniumTestBase
from tests.factories.user import UserFactory


class TestLoginLogout(SeleniumTestBase):
    ''' Test class for user login and logout functionality '''

    def setUp(self):
        # call parent setUp method in SeleniumTestBase class
        super(TestLoginLogout, self).setUp()
        # create a user object from test factory
        self.test_user_password = 'password123'
        # you can manually pass in different parameters to the factory if you
        # want to override the default values. this is useful here since we
        # need the original password string value
        self.test_user = UserFactory(password=self.test_user_password)

    @screenshot_exceptions
    def test_user_login(self):
        ''' test successful login functionality through login form '''
        self.login_user(self.test_user.email, self.test_user_password)

        # verify that browser redirects to user dashboard page after login
        self.assertIn(
            url_for('main.user', username=self.test_user.username),
            self.driver.current_url
        )

        # verify register link is no longer in navigation bar
        with self.assertRaises(NoSuchElementException):
            self.driver.find_element_by_partial_link_text('Register')

    @screenshot_exceptions
    def test_nonexistent_user_login(self):
        ''' test login of non-existent user through login form '''
        self.login_user('idontexist@test.com', 'test')

        msg = 'invalid username or password'
        self.assertTrue(
            self.driver.find_element_by_xpath(
                '//strong[contains(text(),"{}")]'.format(msg))
        )

    @screenshot_exceptions
    def test_user_login_form_validation(self):
        ''' test login form error handling '''

        # test no email address
        self.login_user('', 'test')

        msg = 'Email is required'
        self.assertTrue(
            self.driver.find_element_by_xpath(
                '//p[contains(text(),"{}")]'.format(msg))
        )

        # test no password
        self.login_user(self.test_user.email, '')

        msg = 'Password is required'
        self.assertTrue(
            self.driver.find_element_by_xpath(
                '//p[contains(text(),"{}")]'.format(msg))
        )

        # test invalid email
        self.login_user('invalidemail', 'test')

        msg = 'Invalid email address'
        self.assertTrue(
            self.driver.find_element_by_xpath(
                '//p[contains(text(),"{}")]'.format(msg))
        )

        # test invalid password
        self.login_user(self.test_user.email, '1')

        msg = 'invalid username or password'
        self.assertTrue(
            self.driver.find_element_by_xpath(
                '//strong[contains(text(),"{}")]'.format(msg))
        )

    @screenshot_exceptions
    def test_user_logout(self):
        ''' test basic logout functionality through logout link '''
        self.login_user(self.test_user.email, self.test_user_password)

        logout_link = self.wait().until(
            EC.presence_of_element_located(
                (By.PARTIAL_LINK_TEXT, 'Logout'))
        )
        logout_link.click()

        time.sleep(2)

        # verify that browser redirects to index/home page after logout
        self.assertIn(url_for('main.index'), self.driver.current_url)


class TestRegister(SeleniumTestBase):
    ''' Test class for user registration functionality '''

    def navigate_to_registration(self):
        ''' navigate to user registration page for reuse in tests '''
        register_link = self.wait().until(
            EC.presence_of_element_located(
                (By.PARTIAL_LINK_TEXT, 'Register'))
        )
        register_link.click()

    def register_new_user(self, email, username, password, password_confirm):
        ''' register new user method for reuse in tests '''
        self.navigate_to_registration()

        # complete registration form fields and click register button
        email_field = self.wait().until(
            EC.presence_of_element_located((By.ID, 'email'))
        )
        email_field.send_keys(email)

        username_field = self.driver.find_element_by_id('username')
        username_field.send_keys(username)

        password_field = self.driver.find_element_by_id('password')
        password_field.send_keys(password)

        confirm_password_field = self.driver.find_element_by_id('password2')
        confirm_password_field.send_keys(password_confirm)

        # wait for form info to populate before clicking form submit button
        time.sleep(1)

        login_button = self.driver.find_element_by_xpath('//button[contains(text(),"Register")]')
        login_button.click()

        # wait for server to process form submission and redirect
        time.sleep(3)

    @screenshot_exceptions
    def test_register(self):
        ''' test successful new user registration functionality '''
        self.navigate_to_registration()

        time.sleep(1)

        # verify we are on the registration page
        self.assertIn(url_for('auth.register'), self.driver.current_url)

        self.register_new_user('newuser@test.com', 'newuser', 'newuserpass', 'newuserpass')

        # verify browser redirect home/index page after successful registration
        self.assertIn(url_for('main.index'), self.driver.current_url)

        # verify confirmation message of successful registration
        msg = 'A confirmation email has been sent to you by email'
        self.assertTrue(
            self.driver.find_element_by_xpath(
                '//strong[contains(text(),"{}")]'.format(msg))
        )

    @screenshot_exceptions
    def test_register_form_validation(self):
        ''' test register form error handling '''

        # test no email address
        self.register_new_user('', 'newuser', 'newuserpass', 'newuserpass')

        msg = 'Email is required'
        self.assertTrue(
            self.driver.find_element_by_xpath(
                '//p[contains(text(),"{}")]'.format(msg))
        )

        # test no username
        self.register_new_user('newuser@test.com', '', 'newuserpass', 'newuserpass')

        msg = 'Username is required'
        self.assertTrue(
            self.driver.find_element_by_xpath(
                '//p[contains(text(),"{}")]'.format(msg))
        )

        # test no password
        self.register_new_user('newuser@test.com', 'newuser', '', 'newuserpass')

        msg = 'Password is required'
        self.assertTrue(
            self.driver.find_element_by_xpath(
                '//p[contains(text(),"{}")]'.format(msg))
        )

        # test no password confirmation
        self.register_new_user('newuser@test.com', 'newuser', 'newuserpass', '')

        msg = 'Password match is required'
        self.assertTrue(
            self.driver.find_element_by_xpath(
                '//p[contains(text(),"{}")]'.format(msg))
        )

        # test passwords don't match
        self.register_new_user('newuser@test.com', 'newuser', 'newuserpass', '2132sweg')

        msg = 'Passwords must match'
        self.assertTrue(
            self.driver.find_element_by_xpath(
                '//p[contains(text(),"{}")]'.format(msg))
        )

        # test invalid email
        self.register_new_user('invalidemail', 'newuser', 'newuserpass', 'newuserpass')

        msg = 'Invalid email address'
        self.assertTrue(
            self.driver.find_element_by_xpath(
                '//p[contains(text(),"{}")]'.format(msg))
        )

        # test invalid password
        self.register_new_user('newuser@test.com', 'newuser', 'pass', 'pass')

        msg = 'Passwords must be between 8-64 characters'
        self.assertTrue(
            self.driver.find_element_by_xpath(
                '//p[contains(text(),"{}")]'.format(msg))
        )

    @screenshot_exceptions
    def test_existing_email_registration(self):
        ''' test registration with existing email address '''
        self.navigate_to_registration()

        # create user with email address to reuse
        test_user = UserFactory()

        self.register_new_user(test_user.email, 'newuser', 'newuserpass', 'newuserpass')

        msg = 'Email already registered'
        self.assertTrue(
            self.driver.find_element_by_xpath(
                '//p[contains(text(),"{}")]'.format(msg))
        )

    @screenshot_exceptions
    def test_existing_username_registration(self):
        ''' test registration with existing username '''
        self.navigate_to_registration()

        # create user with username to reuse
        test_user = UserFactory()

        self.register_new_user('newuser@test.com', test_user.username, 'newuserpass', 'newuserpass')

        msg = 'Username already registered'
        self.assertTrue(
            self.driver.find_element_by_xpath(
                '//p[contains(text(),"{}")]'.format(msg))
        )

    @screenshot_exceptions
    def test_forbidden_username_registration(self):
        ''' test registration with forbidden username '''
        self.navigate_to_registration()

        self.register_new_user('newuser@test.com', 'register', 'newuserpass', 'newuserpass')

        msg = 'Please choose a different username'
        self.assertTrue(
            self.driver.find_element_by_xpath(
                '//p[contains(text(),"{}")]'.format(msg))
        )

    @screenshot_exceptions
    def test_special_character_username_registration(self):
        ''' test registration with username containing special characters '''
        self.navigate_to_registration()

        self.register_new_user('newuser@test.com', '!!!', 'newuserpass', 'newuserpass')

        msg = 'Usernames can only contain letters and numbers'
        self.assertTrue(
            self.driver.find_element_by_xpath(
                '//p[contains(text(),"{}")]'.format(msg))
        )

class TestChangePassword(SeleniumTestBase):
    ''' Test class for changing user password functionality '''

    def setUp(self):
        super(TestChangePassword, self).setUp()
        self.test_user_password = 'password123'
        self.test_user = UserFactory(password=self.test_user_password)

    def navigate_to_change_password(self):
        ''' navigate to change password page for reuse in tests '''

        # login user first to get to user dashboard page
        self.login_user(self.test_user.email, self.test_user_password)

        # click on edit profile link on user dash
        edit_profile_link = self.wait().until(
            EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, 'Settings'))
        )
        edit_profile_link.click()

        # navigate to change password page
        change_password_link = self.wait().until(
            EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, 'Change Password'))
        )
        change_password_link.click()

    def change_user_password(self, old_password, new_password, confirm_password):
        ''' change user password form method for reuse in tests '''

        # enter valid values in all fields
        old_password_field = self.wait().until(
            EC.presence_of_element_located((By.ID, 'old_password'))
        )
        old_password_field.send_keys(old_password)

        new_password_field = self.driver.find_element_by_id('password')
        new_password_field.send_keys(new_password)

        confirm_password_field = self.driver.find_element_by_id('password2')
        confirm_password_field.send_keys(confirm_password)

        time.sleep(1)

        change_password_button = self.driver.find_element_by_xpath(
            '//button[contains(text(),"Change Password")]')
        change_password_button.click()

        time.sleep(2)

    @screenshot_exceptions
    def test_change_password(self):
        ''' test change existing user password '''
        self.navigate_to_change_password()

        self.change_user_password(
            self.test_user_password,
            self.test_user_password + '1',
            self.test_user_password + '1')

        # verify message that password change was successful, and redirect
        msg = 'Your password has been updated'
        self.assertTrue(self.driver.find_element_by_xpath(
            '//strong[contains(text(),"{}")]'.format(msg)))
        self.assertIn(url_for('main.edit_profile'), self.driver.current_url)

    @screenshot_exceptions
    def test_change_password_form_validation(self):
        ''' test change password form error handling '''

        self.navigate_to_change_password()

        self.change_user_password(self.test_user_password, '111', '123')

        msg = 'Passwords must match'
        self.assertTrue(self.driver.find_element_by_xpath(
            '//p[contains(text(),"{}")]'.format(msg)))

        self.change_user_password(self.test_user_password, '', '')

        msg = 'This field is required'
        self.assertTrue(self.driver.find_element_by_xpath(
            '//p[contains(text(),"{}")]'.format(msg)))

class TestResetPassword(SeleniumTestBase):
    ''' Test class for resetting user password functionality '''

    def setUp(self):
        super(TestResetPassword, self).setUp()
        self.test_user_password = 'password123'
        self.test_user = UserFactory(password=self.test_user_password)

    def navigate_to_reset_password(self):
        ''' navigate to reset password page for reuse in tests '''

        # click on reset password link to navigate to reset password form
        reset_password_link = self.wait().until(
            EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, 'Forgot your password'))
        )
        reset_password_link.click()

    def reset_user_password(self, email):
        ''' reset user password form method for reuse in tests '''
        self.navigate_to_reset_password()

        # enter email address in email field
        email_field = self.wait().until(
            EC.presence_of_element_located((By.ID, 'email'))
        )
        email_field.send_keys(email)

        # click on reset password button to submit form
        reset_button_path = '//button[contains(text(),"Reset Password")]'
        reset_password_button = self.wait().until(
            EC.presence_of_element_located((By.XPATH, reset_button_path))
        )
        reset_password_button.click()

        time.sleep(2)

    @screenshot_exceptions
    def test_reset_password(self):
        ''' test reset user password '''
        self.reset_user_password(self.test_user.email)

        msg = 'An email with instructions has been sent to you'
        self.assertTrue(self.driver.find_element_by_xpath(
            '//strong[contains(text(),"{}")]'.format(msg)))

    @screenshot_exceptions
    def test_reset_password_form_validation(self):
        ''' test reset password form error handling '''
        self.reset_user_password('abc')

        msg = 'Invalid email address'
        self.assertTrue(self.driver.find_element_by_xpath(
            '//p[contains(text(),"{}")]'.format(msg)))

    @screenshot_exceptions
    def test_reset_password_nonexistent_email(self):
        ''' test reset password with nonexistent email '''
        self.reset_user_password('nonexistent@test.com')

        msg = 'There is no account associated with that email address'
        self.assertTrue(self.driver.find_element_by_xpath(
            '//strong[contains(text(),"{}")]'.format(msg)))

class TestAdminEditProfile(SeleniumTestBase):
    ''' Test class for editing profiles as an admin '''

    def setUp(self):
        # call parent setUp method in SeleniumTestBase class
        super(TestAdminEditProfile, self).setUp()
        # create a user object from test factory
        self.test_user_password = 'password123'
        # you can manually pass in different parameters to the factory if you
        # want to override the default values. this is useful here since we
        # need the original password string value

        # Admin test user
        self.test_user = UserFactory(
            password=self.test_user_password,
            role_id = 1,
            role = Role.query.filter_by(name="admin").first()
        )

        # Non-admin user
        self.test_nonadmin_user = UserFactory(
            username="nonadmin",
            password = self.test_user_password,
            role_id=2,
            role = Role.query.filter_by(name="user").first()
        )

    def navigate_to_admin_settings(self):
        ''' navigate to own admin settings page for reuse in tests '''

        # Login 
        self.login_user(self.test_user.email, self.test_user_password)

        # click on admin settings link to navigate to admin settings page
        admin_settings_link = self.wait().until(
            EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, 'Admin Settings'))
        )
        admin_settings_link.click()

    def navigate_to_other_users_settings(self):
        ''' navigate to other users admin settings page for reuse in tests '''

        # Login
        self.login_user(self.test_user.email, self.test_user_password)

        # go to users page
        users_page_link = self.wait().until(
            EC.presence_of_element_located((By.LINK_TEXT, 'Users'))
        )
        users_page_link.click()

        # Go to non admin users profile page
        users_settings_page_link = self.wait().until(
            EC.presence_of_element_located((By.LINK_TEXT, self.test_nonadmin_user.username))
        )
        users_settings_page_link.click()

        # Go to non admin users edit profile page
        users_settings_page_link = self.wait().until(
            EC.presence_of_element_located((By.LINK_TEXT, 'Admin Settings'))
        )
        users_settings_page_link.click()        


    @screenshot_exceptions
    def test_admin_has_correct_role_on_own_settings_page(self):
        self.navigate_to_admin_settings()

        # Admin option is selected
        self.assertTrue(self.driver.find_element_by_css_selector(
            'select[name="role"] option[value="1"][selected=""]'))

        # User option is not selected
        with self.assertRaises(NoSuchElementException):
            self.driver.find_element_by_css_selector(
            'select[name="role"] option[value="2"][selected=""]')

    @screenshot_exceptions
    def test_user_has_correct_role_viewing_settings_as_admin(self):
        self.navigate_to_other_users_settings()

        # User option is selected
        self.assertTrue(self.driver.find_element_by_css_selector(
            'select[name="role"] option[value="2"][selected=""]'))

        # Admin option is not selected
        with self.assertRaises(NoSuchElementException):
            self.driver.find_element_by_css_selector(
            'select[name="role"] option[value="1"][selected=""]')
