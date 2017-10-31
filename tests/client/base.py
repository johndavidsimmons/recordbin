from datetime import datetime
from functools import wraps
import inspect
import os
import sys
import time
import urllib2

from flask_testing import LiveServerTestCase
from selenium import webdriver
from selenium.common import exceptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from app import create_app, db
from tests.factories.user import UserFactory

# Using flask_testing LiveServerTestCase to run a dev server for local browser testing
# docs can be found here: http://flask-testing.readthedocs.io/en/latest/

# all possible selenium exception types
selenium_exception_classes = tuple(
    x[1] for x in inspect.getmembers(exceptions, inspect.isclass))


def screenshot_exceptions(fn):
    ''' decorator to catch any exceptions in tests and capture a screenshot '''
    @wraps(fn)
    def wrapped(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        # FYI, catching the most generic exception class like this is normally not best practice
        # in the majority of cases, you will want to catch specific exception classes instead
        # of this catch all. Because we are re-raising the exception in this case, it is okay
        except Exception as e:
            # check if its a selenium exception before taking a screenshot
            # (no reason to take a screenshot otherwise)
            if isinstance(e, selenium_exception_classes):
                now = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
                args[0].driver.save_screenshot(
                    'tests/client/screenshots/{}-failure-{}.png'.format(fn.__name__, now))
            # get original exception information, including stacktrace
            exc_info = sys.exc_info()
            # raise original exception with associated info
            raise exc_info[0], exc_info[1], exc_info[2]
    return wrapped


class SeleniumTestBase(LiveServerTestCase):

    def setUp(self):
        db.create_all()
        # initialize webdriver with phantomjs
        self.driver = webdriver.PhantomJS()
        self.driver.set_window_size(1024, 768)
        self.driver.get(self.get_server_url())

    def tearDown(self):
        self.driver.quit()
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def create_app(self):
        ''' required method when inheriting from flask_testing module '''
        app = create_app('testing')
        app.secret_key = 'testing'
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['LIVESERVER_PORT'] = int(os.environ.get('LIVESERVER_PORT', 5000))
        app.config['LIVESERVER_TIMEOUT'] = int(os.environ.get('LIVESERVER_TIMEOUT', 10))
        self.app_context = app.app_context()
        self.app_context.push()
        return app

    def wait(self):
        ''' I'm replacing some of the time.sleeps with this as it is better practice
        Honestly, time.sleep fine is too and more appropriate in some situtions,
        but this is a great tool as well. It will make things run slightly faster as well.
        '''
        return WebDriverWait(self.driver, 10)

    def test_server_sanity(self):
        ''' sanity check to ensure local dev server is running '''
        response = urllib2.urlopen(self.get_server_url())
        self.assertEqual(response.code, 200)

    # now moving this up to the Selenium base class as many of the main views will need
    # a user login method
    def login_user(self, email, password):
        ''' user login method for reuse in tests '''

        # complete login form fields and click submit button
        email_field = self.wait().until(
            EC.presence_of_element_located((By.ID, 'email'))
        )
        email_field.send_keys(email)
        # you may be wondering why i don't put these on one line. personally,
        # i find it much better to write clear code than concise code.
        # by assigning these to variables, i am able to identify exactly
        # what it is i am retrieving
        password_field = self.wait().until(
            EC.presence_of_element_located((By.ID, 'password'))
        )
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
