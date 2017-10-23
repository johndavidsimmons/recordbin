from datetime import datetime
from functools import wraps
import os
import urllib2

from flask_testing import LiveServerTestCase
from selenium import webdriver

from app import create_app, db
from tests.factories.user import UserFactory

# Using flask_testing LiveServerTestCase to run a dev server for local browser testing
# docs can be found here: http://flask-testing.readthedocs.io/en/latest/


def screenshot_exceptions(fn):
    ''' decorator to catch any exceptions in tests and capture a screenshot '''
    @wraps(fn)
    def wrapped(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except Exception as e:
            now = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            args[0].driver.save_screenshot(
                'tests/client/screenshots/{}-failure-{}.png'.format(fn.__name__, now))
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
