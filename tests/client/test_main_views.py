import os
import time

from flask import url_for
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from app import db
from app.models import Artist, Format, Size, Title
from tests.client.base import screenshot_exceptions, SeleniumTestBase
from tests.factories.user import UserFactory


class TestMainPages(SeleniumTestBase):
    ''' Test class for checking elements of main pages '''

    # i moved this here to match the structure of your app better (auth/views and main/views)
    # and to group all main page tests under one class
    @screenshot_exceptions
    def test_index_page_elements(self):
        ''' verify existance of basic elements on index page '''

        # verify we are at the right url
        self.assertIn(url_for('main.index'), self.driver.current_url)

        # verify title on page
        self.assertEqual(self.driver.title, 'Record Bin')

        # verify login form is present
        self.assertTrue(self.driver.find_element_by_id('email'))
        self.assertTrue(self.driver.find_element_by_id('password'))
        self.assertTrue(self.driver.find_element_by_xpath('//button[@name="submit"]'))

        # verify reset password link is present
        self.assertTrue(self.driver.find_element_by_xpath('//a[@href="/auth/reset"]'))

    @screenshot_exceptions
    def test_about_page(self):
        ''' verify existance of basic elements on about page '''

        # navigate to about page
        about_link = self.driver.find_element_by_xpath('//a[contains(text(),"About")]')
        about_link.click()

        time.sleep(1)

        self.assertIn(url_for('main.about'), self.driver.current_url)

        self.assertIn('About', self.driver.title)

        # check that about link on the nav bar is active
        about_link_path = '//li[@class="active"]//a[contains(text(),"About")]'
        self.assertTrue(self.driver.find_element_by_xpath(about_link_path))

        # verify there is a heading About Record Bin
        self.assertTrue(
            self.driver.find_element_by_xpath('//h1[contains(text(),"About Record Bin")]'))

    @screenshot_exceptions
    def test_all_users_page(self):
        ''' verify existance of basic elements on all users page '''

        # navigate to all users page
        users_link = self.driver.find_element_by_xpath('//a[contains(text(),"Users")]')
        users_link.click()

        time.sleep(1)

        self.assertIn(url_for('main.all_users'), self.driver.current_url)

        self.assertIn('Users', self.driver.title)

        # check that users link on the nav bar is active
        users_link_path = '//li[@class="active"]//a[contains(text(),"Users")]'
        self.assertTrue(self.driver.find_element_by_xpath(users_link_path))

        # verify there is the panel header with All Users
        self.assertTrue(
            self.driver.find_element_by_xpath('//strong[contains(text(),"All Users")]'))


class TestAddRecord(SeleniumTestBase):
    ''' Test class for adding a record functionality '''

    def setUp(self):
        super(TestAddRecord, self).setUp()
        self.test_user_password = 'password123'
        self.test_user = UserFactory(password=self.test_user_password)
        Size.insert_sizes()

    @screenshot_exceptions
    def test_add_record(self):
        ''' verify adding a record functionality '''
        self.login_user(self.test_user.email, self.test_user_password)

        add_link = self.wait().until(
            EC.presence_of_element_located((By.ID, 'add-button'))
        )
        add_link.click()

        # verify there is the panel header with Add Record
        self.assertTrue(
            self.driver.find_element_by_xpath('//strong[contains(text(),"Add Record")]'))

        # complete all new record form fields and click add button
        artist = 'Mumford & Sons'
        artist_field = self.wait().until(
            EC.presence_of_element_located((By.ID, 'artist'))
        )
        artist_field.send_keys(artist)

        title = 'Babel'
        title_field = self.driver.find_element_by_id('title')
        title_field.send_keys(title)

        color_field = self.driver.find_element_by_id('color')
        color_field.send_keys('Black')

        # selecting option in dropdown menu by referencing 'select' parent
        select_size = self.driver.find_element_by_xpath(
            '//select[@name="size"]/option[@value="1"]')
        select_size.click()

        select_year = self.driver.find_element_by_xpath(
            '//select[@name="year"]/option[@value="2017"]')
        select_year.click()

        mail_checkbox = self.driver.find_element_by_id('incoming')
        mail_checkbox.click()

        image_uploader = self.driver.find_element_by_id('addFileSelect')
        image_uploader.send_keys(os.getcwd() + '/image.png')

        notes_field = self.driver.find_element_by_id('notes')
        notes_field.send_keys('test notes')

        # submit form for adding new record
        add_button = self.driver.find_element_by_xpath('//button[@name="submit"]')
        add_button.click()

        time.sleep(2)

        # verify that browser is still on user dashboard page after successful submission
        self.assertIn(
            url_for('main.user', username=self.test_user.username),
            self.driver.current_url
        )

        # check for message that record was added
        msg = '{} - {} added'.format(artist, title)
        self.assertTrue(
            self.driver.find_element_by_xpath(
                '//strong[contains(text(),"{}")]'.format(msg))
        )

        # make sure the Artist was added to the database
        self.assertEquals(
            db.session.query(Artist).filter_by(name=artist).count(), 1)

        # make sure the Title was added to the database and the title owner
        # is correctly assigned to the user
        title_query = db.session.query(Title).filter_by(name=title)
        self.assertEquals(title_query.count(), 1)
        self.assertEquals(title_query.first().owner_id, self.test_user.id)


class TestEditDeleteRecord(SeleniumTestBase):
    ''' Test class for editing and deleting a record functionality '''

    def setUp(self):
        super(TestEditDeleteRecord, self).setUp()
        self.test_user_password = 'password123'
        self.test_user = UserFactory(password=self.test_user_password)
        # pre-populate a record owned by the test user for editing and deletion
        Format.insert_formats()
        Size.insert_sizes()
        self.artist = Artist(name='Mumford')
        db.session.add(self.artist)
        db.session.commit()
        self.title = Title(
            name='Babel', artist_id=self.artist.id, year=1970, format_id=1,
            owner_id=self.test_user.id, mail=0, size_id=1, color='black',
            notes='lorem'
        )
        db.session.add(self.title)
        db.session.commit()

    def navigate_to_edit_record(self):
        ''' logs in user and navigates to the edit record modal '''
        self.login_user(self.test_user.email, self.test_user_password)

        edit_icon = self.wait().until(
            EC.presence_of_element_located((By.CLASS_NAME, 'glyphicon-pencil'))
        )
        edit_icon.click()

        time.sleep(1)

    # @screenshot_exceptions
    # def test_edit_record(self):
    #     ''' verify editing a record functionality '''
    #     self.navigate_to_edit_record()

    #     # verify modal is present and has Edit Record as the title
    #     self.assertTrue(self.driver.find_element_by_class_name('modal-title'))
    #     self.assertEquals(
    #         self.driver.find_element_by_class_name('modal-title').text, 'Edit Record')

    #     # complete all new record form fields and click add button
    #     artist = 'Of Monsters and Men'
    #     artist_field = self.driver.find_element_by_id('artist')
    #     artist_field.send_keys(artist)

    #     title = 'My Head is an Animal'
    #     title_field = self.driver.find_element_by_id('title')
    #     title_field.send_keys(title)

    #     color_field = self.driver.find_element_by_id('color')
    #     color_field.send_keys('Black')

    #     # selecting option in dropdown menu by referencing 'select' parent
    #     select_size = self.driver.find_element_by_xpath(
    #         '//select[@name="size"]/option[@value="1"]')
    #     select_size.click()

    #     select_year = self.driver.find_element_by_xpath(
    #         '//select[@name="year"]/option[@value="2017"]')
    #     select_year.click()

    #     mail_checkbox = self.driver.find_element_by_id('incoming')
    #     mail_checkbox.click()

    #     image_uploader = self.driver.find_element_by_id('addFileSelect')
    #     image_uploader.send_keys(os.getcwd() + '/image.png')

    #     notes_field = self.driver.find_element_by_id('notes')
    #     notes_field.send_keys('test notes')

    #     # submit form for adding new record
    #     save_button = self.driver.find_element_by_name('edit-record-save')
    #     save_button.click()

    #     time.sleep(1)

    #     # check for confirmation message that record was deleted
    #     msg = '{} - {} Updated!'.format(artist, title)
    #     self.assertTrue(
    #         self.driver.find_element_by_xpath(
    #             '//strong[contains(text(),"{}")]'.format(msg))
    #     )

    #     # make sure the Artist was added to the database
    #     self.assertEquals(
    #         db.session.query(Artist).filter_by(name=artist).count(), 1)

    #     # make sure the Title was added to the database and the title owner
    #     # is correctly assigned to the user
    #     title_query = db.session.query(Title).filter_by(name=title)
    #     self.assertEquals(title_query.count(), 1)
    #     self.assertEquals(title_query.first().owner_id, self.test_user.id)

    # @screenshot_exceptions
    # def test_delete_record(self):
    #     ''' verify deleting a record functionality '''
    #     self.navigate_to_edit_record()

    #     # make sure delete record link is present
    #     self.assertTrue(self.driver.find_element_by_class_name('glyphicon-trash'))

    #     # click on delete record link
    #     delete_link = self.driver.find_element_by_xpath(delete_link_path)
    #     delete_link.click()

    #     time.sleep(1)

    #     # check for confirmation message that record was deleted
    #     msg = '{} - {} Deleted!'.format(self.artist.name, self.title.name)
    #     self.assertTrue(
    #         self.driver.find_element_by_xpath(
    #             '//strong[contains(text(),"{}")]'.format(msg))
    #     )

    #     # make sure the Artist was deleted from the database
    #     self.assertEquals(
    #         db.session.query(Artist).filter_by(name=self.artist.name).count(), 0)

    #     # make sure the Title was deleted from the database
    #     self.assertEquals(
    #         db.session.query(Title).filter_by(name=self.artist.name).count(), 0)
