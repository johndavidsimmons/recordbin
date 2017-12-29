import os
import time
from datetime import datetime

from flask import url_for
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

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
        self.assertTrue(self.driver.find_element_by_id('remember_me'))
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
        Format.insert_formats()

    @screenshot_exceptions
    def test_add_record(self):
        ''' verify adding a record functionality '''
        # upload photo - add_image_url value is cloud url
        self.login_user(self.test_user.email, self.test_user_password)

        add_link = self.wait().until(
            EC.presence_of_element_located((By.ID, 'add-button'))
        )

        if add_link.is_displayed():
            add_link.click()

        # verify there is the panel header with Add Record
        self.assertTrue(
            self.driver.find_element_by_xpath('//strong[contains(text(),"Add Record")]').is_displayed())

        # Verify the add button now has the disabled class
        self.assertTrue(
            self.driver.find_element_by_css_selector('#add-button.disabled').is_displayed()
        )

        # complete all new record form fields and click add button
        artist = 'Mumford & Sons'
        artist_field = self.wait().until(
            EC.presence_of_element_located((By.ID, 'artist'))
        )
        artist_field.send_keys(artist)

        title = 'Babel'
        title_field = self.driver.find_element_by_id('title')
        title_field.send_keys(title)

        color = "Black"
        color_field = self.driver.find_element_by_id('color')
        color_field.send_keys(color)

        # selecting option in dropdown menu by referencing 'select' parent
        select_size = self.driver.find_element_by_xpath(
            '//select[@name="size"]/option[@value="1"]')
        select_size.click()

        select_year = self.driver.find_element_by_xpath(
            '//select[@name="year"]/option[@value="2000"]')
        select_year.click()

        # mail_checkbox = self.driver.find_element_by_id('incoming')
        # mail_checkbox.click()

        # image_uploader = self.driver.find_element_by_id('addFileElem')
        # image_uploader.send_keys(os.getcwd() + '/image.png')

        notes = "test notes"
        notes_field = self.driver.find_element_by_id('notes')
        notes_field.send_keys(notes)

        # submit form for adding new record
        add_button = self.driver.find_element_by_css_selector("button[name='submit']")
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

        # Check that the record is added to the 7inch table, non-incoming and all data is present
        # Artist
        element = self.driver.find_element_by_xpath("//*[@id='seven_inches']//td[contains(text(),'{}')]".format(artist))
        self.assertTrue(
            element.is_displayed()
        )
        # Title
        element = self.driver.find_element_by_xpath("//*[@id='seven_inches']//td[contains(text(),'{}')]".format(title))
        self.assertTrue(
            element.is_displayed()
        )

        # color
        element = self.driver.find_element_by_xpath("//*[@id='seven_inches']//td[contains(text(),'{}')]".format(color))
        self.assertTrue(
            element.is_displayed()
        )

        # year
        element = self.driver.find_element_by_xpath("//*[@id='seven_inches']//td[contains(text(),'{}')]".format("2000"))
        self.assertTrue(
            element.is_displayed()
        )

        # notes
        element = self.driver.find_element_by_xpath("//*[@id='seven_inches']//td[contains(text(),'{}')]".format(notes))
        self.assertTrue(
            element.is_displayed()
        )

        # timestamp
        timestamp = datetime.now().strftime('%-m/%-d/%y')
        element = self.driver.find_element_by_xpath("//*[@id='seven_inches']//td[contains(text(),'{}')]".format(timestamp))
        self.assertTrue(
            element.is_displayed()
        )

        # Make sure the user's record count goes up in 2 places
        # profile
        element = self.driver.find_element_by_xpath("//span[contains(@class,'label-primary') and text() = '1 Record']")
        self.assertTrue(
            element.is_displayed()
        )
        # table
        element = self.driver.find_element_by_xpath("//span[contains(@class,'badge') and text() = '1']")
        self.assertTrue(
            element.is_displayed()
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

        # Non mail record
        self.title = Title(
            name='Babel', artist_id=self.artist.id, year=1970, format_id=1,
            owner_id=self.test_user.id, mail=0, size_id=1, color='black',
            notes='lorem'
        )
        db.session.add(self.title)
        db.session.commit()


        # these are necessary for when a record is deleted
        self.artist_name = self.artist.name
        self.title_name = self.title.name

    def navigate_to_edit_record(self):
        ''' logs in user and navigates to the edit record modal '''
        self.login_user(self.test_user.email, self.test_user_password)

        # This is done via JS, using Selenium can't find it for some reason
        self.driver.execute_script('''document.querySelector(".glyphicon-pencil").click();''')
        
        time.sleep(1)

    @screenshot_exceptions
    def test_edit_record(self):
        ''' verify editing a record functionality '''
        self.navigate_to_edit_record()

        time.sleep(1)

        # verify modal is present and has Edit Record as the title
        self.assertTrue(self.driver.find_element_by_class_name('modal-title'))
        self.assertEquals(
            self.driver.find_element_by_class_name('modal-title').text, 'Edit Record')

        # complete all new record form fields and click add button
        artist = 'Of Monsters and Men'
        artist_field = self.driver.find_element_by_id('edit_artist')
        artist_field.clear()
        artist_field.send_keys(artist)

        title = 'My Head is an Animal'
        title_field = self.driver.find_element_by_id('edit_title')
        title_field.clear()
        title_field.send_keys(title)

        color = "Yellow"
        color_field = self.driver.find_element_by_id('edit_color')
        color_field.clear()
        color_field.send_keys(color)


        # selecting option in dropdown menu by referencing 'select' parent
        select_size = self.driver.find_element_by_xpath(
            # //select[@name='element_name']/option[text()='option_text']"
            '//select[@name="edit_size"]/option[text()="10"]')
        select_size.click()

        select_year = self.driver.find_element_by_xpath(
            '//select[@name="edit_year"]/option[text()="2010"]')
        select_year.click()

        # mail_checkbox = self.driver.find_element_by_id('edit_incoming')
        # mail_checkbox.click()

        # image_uploader = self.driver.find_element_by_id('fileSelect')
        # image_uploader.send_keys(os.getcwd() + '/image.png')

        notes_field = self.driver.find_element_by_id('edit_notes')
        notes_field.send_keys('swag notes')

        # submit form for editing record
        save_button = self.wait().until(
            EC.presence_of_element_located((By.NAME, 'edit-record-save'))
        )
        save_button.click()

        time.sleep(2)

        # check for confirmation message that record was Updated
        msg = '{} - {} Updated!'.format(artist, title)
        self.assertTrue(
            self.driver.find_element_by_xpath(
                '//strong[contains(text(),"{}")]'.format(msg))
        )

        # Make sure the table elements reflect the new values
        # Artist
        element = self.driver.find_element_by_xpath("//*[@id='ten_inches']//td[contains(text(),'{}')]".format(artist))
        self.assertTrue(
            element.is_displayed()
        )

        # Title
        element = self.driver.find_element_by_xpath("//*[@id='ten_inches']//td[contains(text(),'{}')]".format(title))
        self.assertTrue(
            element.is_displayed()
        )

        # Color
        element = self.driver.find_element_by_xpath("//*[@id='ten_inches']//td[contains(text(),'{}')]".format(color))
        self.assertTrue(
            element.is_displayed()
        )

        # make sure the Artist was added to the database
        self.assertEquals(
            db.session.query(Artist).filter_by(name=artist).count(), 1)

        # make sure the Title was added to the database and the title owner
        # is correctly assigned to the user
        title_query = db.session.query(Title).filter_by(name=title)
        self.assertEquals(title_query.count(), 1)
        self.assertEquals(title_query.first().owner_id, self.test_user.id)

    @screenshot_exceptions
    def test_delete_record(self):
        ''' verify deleting a record functionality '''
        self.navigate_to_edit_record()

        # make sure delete record link is present
        # Side Note - the reason I don't assign this to a variable first (since I'm referencing
        # the same element again below) is I want it to fail on the assertion, not the assignment
        self.assertTrue(self.driver.find_element_by_xpath('//a[contains(@href,"delete-record")]'))

        # click on delete record link
        # PhantomJS can't find it
        self.driver.execute_script(''' document.querySelector('.glyphicon-trash').click(); ''')

        time.sleep(1)

        # check for confirmation message that record was deleted
        msg = '{} - {} Deleted!'.format(self.artist_name, self.title_name)
        self.assertTrue(
            self.driver.find_element_by_xpath(
                '//strong[contains(text(),"{}")]'.format(msg))
        )

        # verify the page elements are gone
        # Artist
        with self.assertRaises(NoSuchElementException):
            element = self.driver.find_element_by_xpath("//*[@id='seven_inches']//td[contains(text(),'{}')]".format(self.artist_name))

        # title
        with self.assertRaises(NoSuchElementException):
            element = self.driver.find_element_by_xpath("//*[@id='seven_inches']//td[contains(text(),'{}')]".format(self.title_name))

        # make sure the Artist was not deleted from the database
        self.assertEquals(
            db.session.query(Artist).filter_by(name=self.artist_name).count(), 1)

        # make sure the Title was deleted from the database
        self.assertEquals(
            db.session.query(Title).filter_by(name=self.title_name).count(), 0)

    @screenshot_exceptions
    def test_incoming_move_tables(self):
        ''' verify editing a record functionality '''
        self.navigate_to_edit_record()

        time.sleep(1)

        # verify modal is present and has Edit Record as the title
        self.assertTrue(self.driver.find_element_by_class_name('modal-title'))
        self.assertEquals(
            self.driver.find_element_by_class_name('modal-title').text, 'Edit Record')

        # Check the mail box
        mail_checkbox = self.driver.find_element_by_id('edit_incoming')
        mail_checkbox.click()

        # submit form for editing record
        save_button = self.wait().until(
            EC.presence_of_element_located((By.NAME, 'edit-record-save'))
        )
        save_button.click()

        time.sleep(2)

        # check for confirmation message that record was Updated
        msg = '{} - {} Updated!'.format(self.artist_name, self.title_name)
        self.assertTrue(
            self.driver.find_element_by_xpath(
                '//strong[contains(text(),"{}")]'.format(msg))
        )

        # Assert the record is in the mail table now
        # Artist
        try:
            element = self.driver.find_element_by_xpath("//*[@id='seven_inches_mail']//td[contains(text(),'{}')]".format(self.artist_name))
        except NoSuchElementException:
            self.fail("Failed with NoSuchElementException")

        # title
        try:
            element = self.driver.find_element_by_xpath("//*[@id='seven_inches_mail']//td[contains(text(),'{}')]".format(self.title_name))
        except NoSuchElementException:
            self.fail("Failed with NoSuchElementException")   

        
        # Move it back to the regular table

        # This is done via JS, using Selenium can't find it for some reason
        self.driver.execute_script('''document.querySelector(".glyphicon-pencil").click();''')

        time.sleep(1)
        self.assertTrue(self.driver.find_element_by_class_name('modal-title'))
        self.assertEquals(
            self.driver.find_element_by_class_name('modal-title').text, 'Edit Record')

        # uncheck the mail box
        mail_checkbox = self.driver.find_element_by_id('edit_incoming')
        mail_checkbox.click()

        # submit form for editing record
        save_button = self.wait().until(
            EC.presence_of_element_located((By.NAME, 'edit-record-save'))
        )
        save_button.click()

        # Elements are in the non-mail table
        # artist
        try:
            element = self.driver.find_element_by_xpath("//*[@id='seven_inches']//td[contains(text(),'{}')]".format(self.artist_name))
        except NoSuchElementException:
            self.fail("Failed with NoSuchElementException")

        # title
        try:
            element = self.driver.find_element_by_xpath("//*[@id='seven_inches']//td[contains(text(),'{}')]".format(self.title_name))
        except NoSuchElementException:
            self.fail("Failed with NoSuchElementException")


class TestFilterRecordTable(SeleniumTestBase):
    ''' Test class for filtering records in the table '''
    # the filter bar is visible
    # only the certain tds are visible
    # assert the count label appears and is correct
    # clearing the field hides the lable count
        # keys
        # clear button X
    # clearing the field shows all tds
        # keys
        # clear button x
    # an invalid query hides all tds
    # an invalid query shows a 0 in the label

    def setUp(self):
        super(TestFilterRecordTable, self).setUp()
        self.test_user_password = 'password123'
        self.test_user = UserFactory(password=self.test_user_password)
        # pre-populate a few records owned by the test user for filtering
        Format.insert_formats()
        Size.insert_sizes()
        
        artists = [
            Artist(name='Black Sabbath'), 
            Artist(name='Thin Lizzy'), 
            Artist(name='Daft Punk'),
        ]

        for artist in artists:
            db.session.add(artist)
        db.session.commit()

        records = [
            Title(
                name='Paranoid', artist_id=1, year=1970, format_id=1,
                owner_id=self.test_user.id, mail=0, size_id=1, color='black',
                notes='lorem'
            ),
            Title(
                name='Jailbreak', artist_id=2, year=1970, format_id=1,
                owner_id=self.test_user.id, mail=0, size_id=2, color='black',
                notes='lorem'
            ),
            Title(
                name='RAM', artist_id=3 , year=1970, format_id=1,
                owner_id=self.test_user.id, mail=0, size_id=3, color='black',
                notes='lorem'
            ),
        ]

        for title in records:
            db.session.add(title)
        db.session.commit()

    @screenshot_exceptions
    def test_filter_bar_exists(self):
        self.login_user(self.test_user.email, self.test_user_password)

        # filter bar
        element = self.driver.find_element_by_id("search")
        self.assertTrue(
            element.is_displayed()
        )

    # @screenshot_exceptions
    # def test_keypress_filters_records(self):
    #     self.assertTrue(False)
    #     # self.login_user(self.test_user.email, self.test_user_password)
    #     # search_bar = self.driver.find_element_by_id("search")
    #     # search_bar.send_keys("black")
    #     # self.driver.find_element_by_id('dfds')
    #     # self.driver.execute_script('''''')
        
class TestProfileBadges(SeleniumTestBase):
    ''' 
    Test the elements of the users profile badges 
    - Number of records 0, 1, (2+ done on line)
    - Number of followers
    - Number of users followed
    '''

    def setUp(self):
        super(TestProfileBadges, self).setUp()
        self.test_user_password = 'password123'
        self.test_user = UserFactory(password=self.test_user_password)
        Size.insert_sizes()
        Format.insert_formats()

    @screenshot_exceptions
    def test_badge_correct_zero_records(self):
        self.login_user(self.test_user.email, self.test_user_password)

        element = self.driver.find_element_by_xpath("//span[contains(@class,'label-primary') and text() = '0 Records']")
        self.assertTrue(
            element.is_displayed()
        )

    @screenshot_exceptions
    def test_badge_correct_2plus_records(self):
        self.login_user(self.test_user.email, self.test_user_password)

        # Add 2 records
        add_link = self.wait().until(
            EC.presence_of_element_located((By.ID, 'add-button'))
        )

        if add_link.is_displayed():
            add_link.click()

        # complete all new record form fields and click add button
        artist = 'Mumford & Sons'
        artist_field = self.wait().until(
            EC.presence_of_element_located((By.ID, 'artist'))
        )
        artist_field.send_keys(artist)

        title = 'Babel'
        title_field = self.driver.find_element_by_id('title')
        title_field.send_keys(title)

        color = "Black"
        color_field = self.driver.find_element_by_id('color')
        color_field.send_keys(color)

        # selecting option in dropdown menu by referencing 'select' parent
        select_size = self.driver.find_element_by_xpath(
            '//select[@name="size"]/option[@value="1"]')
        select_size.click()

        select_year = self.driver.find_element_by_xpath(
            '//select[@name="year"]/option[@value="2000"]')
        select_year.click()

        # mail_checkbox = self.driver.find_element_by_id('incoming')
        # mail_checkbox.click()

        # image_uploader = self.driver.find_element_by_id('addFileElem')
        # image_uploader.send_keys(os.getcwd() + '/image.png')

        notes = "test notes"
        notes_field = self.driver.find_element_by_id('notes')
        notes_field.send_keys(notes)

        # submit form for adding new record
        add_button = self.driver.find_element_by_css_selector("button[name='submit']")
        add_button.click()

        time.sleep(2)

        add_link = self.wait().until(
            EC.presence_of_element_located((By.ID, 'add-button'))
        )

        if add_link.is_displayed():
            add_link.click()

        # complete all new record form fields and click add button
        artist = 'Mumford & Sons'
        artist_field = self.wait().until(
            EC.presence_of_element_located((By.ID, 'artist'))
        )
        artist_field.send_keys(artist)

        title = 'Babel2'
        title_field = self.driver.find_element_by_id('title')
        title_field.send_keys(title)

        color = "Black"
        color_field = self.driver.find_element_by_id('color')
        color_field.send_keys(color)

        # selecting option in dropdown menu by referencing 'select' parent
        select_size = self.driver.find_element_by_xpath(
            '//select[@name="size"]/option[@value="1"]')
        select_size.click()

        select_year = self.driver.find_element_by_xpath(
            '//select[@name="year"]/option[@value="2000"]')
        select_year.click()

        # mail_checkbox = self.driver.find_element_by_id('incoming')
        # mail_checkbox.click()

        # image_uploader = self.driver.find_element_by_id('addFileElem')
        # image_uploader.send_keys(os.getcwd() + '/image.png')

        notes = "test notes"
        notes_field = self.driver.find_element_by_id('notes')
        notes_field.send_keys(notes)

        # submit form for adding new record
        add_button = self.driver.find_element_by_css_selector("button[name='submit']")
        add_button.click()

        time.sleep(2)

        element = self.driver.find_element_by_xpath("//span[contains(@class,'label-primary') and text() = '2 Records']")
        self.assertTrue(
            element.is_displayed()
        )
