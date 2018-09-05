import datetime

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.conf import settings
from django.test import tag
from django.urls import reverse
from selenium.common.exceptions import NoSuchElementException
import pyvirtualdisplay


@tag("selenium")
class FunctionalTestCase(StaticLiveServerTestCase):
    config = settings.FUNCT_TESTS_CONFIG

    @classmethod
    def setUpClass(cls):
        super(FunctionalTestCase, cls).setUpClass()
        if cls.config.get('VIRTUAL_DISPLAY'):
            cls.virtual_display = pyvirtualdisplay.Display(size=(cls.config.get('DISPLAY_WIDTH'),
                                                                 cls.config.get('DISPLAY_HEIGHT')))
            cls.virtual_display.start()

        if cls.config.get('BROWSER') == 'FIREFOX':
            from selenium.webdriver.firefox.webdriver import WebDriver
            cls.selenium = WebDriver(executable_path=cls.config.get('GECKO_DRIVER'))

        if cls.config.get('VIRTUAL_DISPLAY'):
            cls.selenium.implicitly_wait(5)

        cls.selenium.set_window_size(cls.config.get('DISPLAY_WIDTH'), cls.config.get('DISPLAY_HEIGHT'))

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        if cls.config.get('VIRTUAL_DISPLAY'):
            cls.virtual_display.stop()
        super(FunctionalTestCase, cls).tearDownClass()

    def openUrlByName(self, url_name):
        try:
            self.selenium.get(self.live_server_url + reverse(url_name))
        except Exception:
            self.take_screenshot("url_{}_error".format(url_name))
            raise

    def fill_element_by_id(self, element_id, value):
        try:
            element = self.selenium.find_element_by_id(element_id)
            element.clear()
            element.send_keys(value)
        except Exception:
            self.take_screenshot("element_{}_error".format(element_id))
            raise

    def click_element_by_id(self, element_id):
        try:
            element = self.selenium.find_element_by_id(element_id)
            element.click()
        except Exception:
            self.take_screenshot("element_{}_error".format(element_id))
            raise

    def login(self, username, password=None):
        if password is None:
            password = "password123"
        self.openUrlByName('login')
        self.fill_element_by_id('id_username', username)
        self.fill_element_by_id('id_password', password)
        self.click_element_by_id('post_login_btn')

    def check_page_title(self, expected_title):
        try:
            self.assertEqual(self.selenium.title, expected_title)
        except AssertionError:
            self.take_screenshot("title_{}_error".format(expected_title))
            raise

    def check_page_contains_string(self, expected_string):
        try:
            self.assertTrue(expected_string in self.selenium.page_source)
        except AssertionError:
            self.take_screenshot("page_should_contains_{}".format(expected_string))
            raise

    def check_page_not_contains_string(self, expected_string):
        try:
            self.assertFalse(expected_string in self.selenium.page_source)
        except AssertionError:
            self.take_screenshot("page_should_not_contains_{}".format(expected_string))
            raise

    def check_page_contains_ids(self, ids):
        try:
            for id in ids:
                self.selenium.find_element_by_id(id)
        except NoSuchElementException:
            self.take_screenshot("{}_should_be_present_on_page".format(id))
            raise

    def check_page_not_contains_ids(self, ids):
        for id in ids:
            try:
                with self.assertRaises(NoSuchElementException):
                    self.selenium.find_element_by_id(id)
            except AssertionError:
                self.take_screenshot("{}_should_not_be_present_on_page".format(id))
                raise

    def take_screenshot(self, name):
        date_str = "{:%d_%m_%Y}".format(datetime.datetime.today())
        complete_path = "{screenshot_dir}/{name}_{date}.png".format(screenshot_dir=self.config.get('SCREENSHOTS_DIR'),
                                                                    name=name,
                                                                    date=date_str)
        self.selenium.save_screenshot(complete_path)
