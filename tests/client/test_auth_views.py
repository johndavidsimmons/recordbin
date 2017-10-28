import time

from flask import url_for
from selenium.common.exceptions import NoSuchElementException

from app import db
from tests.client.base import screenshot_exceptions, SeleniumTestBase
from tests.factories.user import UserFactory


# I am moving the login_user method to a base class. It makes more sense that way
# since i am having to reference the driver. The login_user would work as a solo function
# as well, but it seems to fit better this way. I also added the tearDown while I was at
# it since its common to all these classes
class TestAuthBase(SeleniumTestBase):

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        # call parent tearDown method in TestAuthBase class
        super(TestAuthBase, self).tearDown()

    def login_user(self, email, password):
        ''' user login method for reuse in tests '''

        # complete login form fields and click submit button
        email_field = self.driver.find_element_by_id('email')
        email_field.send_keys(email)
        # you may be wondering why i don't put these on one line. personally,
        # i find it much better to write clear code than concise code.
        # by assigning these to variables, i am able to identify exactly
        # what it is i am retrieving
        password_field = self.driver.find_element_by_id('password')
        password_field.send_keys(password)

        # these time.sleep functions are necessary to allow the server time to
        # process our request
        time.sleep(1)

        # this find_element_by_xpath is a great utility for finding elements
        # that you cant find using id, class, name, tag, etc. I am using it here
        # for a little flexibility with future development rather than selecting
        # by name. This would be easier to select by more unique html identifiers.
        login_button = self.driver.find_element_by_xpath('//button[contains(text(),"Log In")]')
        login_button.click()

        time.sleep(2)


class TestLoginLogout(TestAuthBase):
    ''' Test class for user login and logout functionality '''

    def setUp(self):
        db.create_all()
        # create a user object from test factory
        self.test_user_password = 'password123'
        # you can manually pass in different parameters to the factory if you
        # want to override the default values. this is useful here since we
        # need the original password string value
        self.test_user = UserFactory(password=self.test_user_password)
        # call parent setUp method in TestAuthBase class
        super(TestLoginLogout, self).setUp()

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
            self.driver.find_element_by_xpath('//a[contains(text(),"Register")]')

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

        logout_link = self.driver.find_element_by_xpath('//a[contains(text(),"Logout")]')
        logout_link.click()

        time.sleep(2)

        # verify that browser redirects to index/home page after logout
        self.assertIn(url_for('main.index'), self.driver.current_url)


class TestRegister(TestAuthBase):
    ''' Test class for user registration functionality '''

    def setUp(self):
        db.create_all()
        super(TestRegister, self).setUp()

    def navigate_to_registration(self):
        ''' navigate to user registration page for reuse in tests '''
        register_link = self.driver.find_element_by_xpath('//a[contains(text(),"Register")]')
        register_link.click()
        time.sleep(2)

    def register_new_user(self, email, username, password, password_confirm):
        ''' register new user method for reuse in tests '''
        self.navigate_to_registration()

        # complete registration form fields and click register button
        email_field = self.driver.find_element_by_id('email')
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


class TestPasswordManagement(TestAuthBase):
    ''' Test class for user password management functionality '''

    def setUp(self):
        db.create_all()
        self.test_user_password = 'password123'
        self.test_user = UserFactory(password=self.test_user_password)
        super(TestPasswordManagement, self).setUp()

    def navigate_to_edit_profile(self):
        ''' navigate to edit profile page for reuse in tests '''

        # login user first to get to user dashboard page
        self.login_user(self.test_user.email, self.test_user_password)

        time.sleep(1)
        # click on edit profile link on user dash
        edit_profile_link = self.driver.find_element_by_xpath('//a[@href="/edit-profile"]')
        edit_profile_link.click()

        time.sleep(2)

    def change_user_password(self, old_password, new_password, confirm_password):
        ''' change user password form method for reuse in tests '''
        self.navigate_to_edit_profile()

        # navigate to change password page
        change_password_link = self.driver.find_element_by_xpath(
            '//a[contains(text(),"Change Password")]')
        change_password_link.click()

        time.sleep(2)

        # enter valid values in all fields
        old_password_field = self.driver.find_element_by_id('old_password')
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
        self.change_user_password(
            self.test_user_password,
            self.test_user_password + '1',
            self.test_user_password + '1')

        # verify message that password change was successful, and redirect
        msg = 'Your password has been updated'
        self.assertTrue(self.driver.find_element_by_xpath(
            '//strong[contains(text(),"{}")]'.format(msg)))
        self.assertIn(url_for('main.edit_profile'), self.driver.current_url)

    def test_change_password_invalid(self):
        ''' test change user password with invalid values '''
        pass

    def test_reset_password(self):
        ''' test reset user password '''
        pass

    def test_reset_password_invalid_email(self):
        ''' test reset password with invalid email '''
        pass
