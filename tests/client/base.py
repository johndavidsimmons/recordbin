from datetime import datetime
from functools import wraps
import inspect
import os
import sys
import urllib2

from flask_testing import LiveServerTestCase
from selenium import webdriver
from selenium.common import exceptions

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
        # initialize webdriver with phantomjs
        self.driver = webdriver.PhantomJS()
        self.driver.set_window_size(1024, 768)
        self.driver.get(self.get_server_url())

    def tearDown(self):
        self.driver.quit()
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

    def test_server_sanity(self):
        ''' sanity check to ensure local dev server is running '''
        response = urllib2.urlopen(self.get_server_url())
        self.assertEqual(response.code, 200)
