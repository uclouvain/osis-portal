from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from base.tests.functional.models.model import FunctionalTestCase
from base.tests.functional.models.user_type import FacAdministratorMixin, AdministratorMixin


class FacAdminPageTestCase(FunctionalTestCase, FacAdministratorMixin):

    def setUp(self):
        super(FacAdminPageTestCase, self).setUp()
        self.fac_admin = self.create_fac_admin()

    def test_fac_admin_page(self):
        """
        As a Faculty Administrator
        - I can go to the "Faculty Administration Page"
        - I should see the links to faculty administration sub pages
        """
        self.login(self.fac_admin.user.username)
        self._got_to_fac_admin_page()
        self.check_page_title(self.config.get('FAC_ADMIN').get('PAGE_TITLE'))
        self.check_page_contains_ids(self.config.get('FAC_ADMIN').get('ADMIN_LINKS'))

    def _got_to_fac_admin_page(self):
        self.openUrlByName('home')
        self.click_element_by_id(self.config.get('FAC_ADMIN').get('FROM_DASH_LINK_1'))
        self.click_element_by_id(self.config.get('FAC_ADMIN').get('FROM_DASH_LINK_2'))


class DataAdminPagesTestCase(FunctionalTestCase, AdministratorMixin):

    def setUp(self):
        super(DataAdminPagesTestCase, self).setUp()
        self.data_admin = self.create_admin()

    def _go_to_data_admin_page(self):
        self.openUrlByName('home')
        self.click_element_by_id(self.config.get('DATA_ADMIN').get('FROM_DASH_LINK_1'))
        self.click_element_by_id(self.config.get('DATA_ADMIN').get('FROM_DASH_LINK_2'))

    def _go_to_data_management_page(self):
        self.openUrlByName('data')
        self.click_element_by_id(self.config.get('DATA_MANAGEMENT').get('FROM_DATA_ADMIN_LNK'))

    def test_data_admin_page(self):
        """
        As a data administrator
        - I can go to the data administration page
        - I should see the links to data administration sub pages
        """
        self.login(self.data_admin.user.username)
        self._go_to_data_admin_page()
        self.check_page_title(self.config.get('DATA_ADMIN').get('PAGE_TITLE'))
        self.check_page_contains_ids(self.config.get('DATA_ADMIN').get('ADMIN_LINKS'))

    def test_data_management_page(self):
        """
        As a data administrator
        - I can go to the data management page
        """
        self.login(self.data_admin.user.username)
        self._go_to_data_management_page()
        self.wait_until_tabs_open()
        tabs = self.selenium.window_handles
        self.selenium.switch_to_window(tabs[1])
        self.check_page_title(self.config.get('DATA_MANAGEMENT').get('PAGE_TITLE'))
