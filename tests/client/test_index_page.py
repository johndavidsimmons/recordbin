from tests.client.base import screenshot_exceptions, SeleniumTestBase


class TestIndexPage(SeleniumTestBase):
    ''' Test class for basic elements of index page '''

    @screenshot_exceptions
    def test_index_page_title(self):
        ''' super basic test just verifying title on index page '''
        self.assertEqual(self.driver.title, 'Record Bin')

    @screenshot_exceptions
    def test_index_login_form_exists(self):
        ''' verify the login fields and button are present on the index page '''
        self.assertTrue(self.driver.find_element_by_id('email'))
        self.assertTrue(self.driver.find_element_by_id('password'))
        self.assertTrue(self.driver.find_element_by_xpath('//button[@name="submit"]'))

    @screenshot_exceptions
    def test_index_reset_password_link_exists(self):
        ''' verify reset password link is present on the index page '''
        self.assertTrue(self.driver.find_element_by_xpath('//a[@href="/auth/reset"]'))
