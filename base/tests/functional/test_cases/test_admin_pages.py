from base.tests.functional.models.model import FunctionalTestCase
from base.tests.functional.models.user_type import FacAdministratorMixin, AdministratorMixin


class FacAdminPageTestCase(FunctionalTestCase, FacAdministratorMixin):

    @classmethod
    def setUpClass(cls):
        super(FacAdminPageTestCase, cls).setUpClass()
        cls.admin_config = cls.config.get('ADMIN')

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
        self.check_page_title(self.admin_config.get('FAC_ADMIN').get('PAGE_TITLE'))
        self.check_page_contains_ids(self.admin_config.get('FAC_ADMIN').get('ADMIN_LINKS'))

    def _got_to_fac_admin_page(self):
        self.openUrlByName('home')
        self.click_element_by_id(self.admin_config.get('FAC_ADMIN').get('FROM_DASH_LINK_1'))
        self.click_element_by_id(self.admin_config.get('FAC_ADMIN').get('FROM_DASH_LINK_2'))


class DataAdminPagesTestCase(FunctionalTestCase, AdministratorMixin):

    @classmethod
    def setUpClass(cls):
        super(DataAdminPagesTestCase, cls).setUpClass()
        cls.data_admin_config = cls.config.get('ADMIN').get('DATA_ADMIN')
        cls.data_management_config = cls.config.get('ADMIN').get('DATA_MANAGEMENT')

    def setUp(self):
        super(DataAdminPagesTestCase, self).setUp()
        self.data_admin = self.create_admin()

    def _go_to_data_admin_page(self):
        self.openUrlByName('home')
        self.click_element_by_id(self.data_admin_config.get('FROM_DASH_LINK_1'))
        self.click_element_by_id(self.data_admin_config.get('FROM_DASH_LINK_2'))

    def _go_to_data_management_page(self):
        self.openUrlByName('data')
        self.click_element_by_id(self.data_management_config.get('FROM_DATA_ADMIN_LNK'))

    def test_data_admin_page(self):
        """
        As a data administrator
        - I can go to the data administration page
        - I should see the links to data administration sub pages
        """
        self.login(self.data_admin.user.username)
        self._go_to_data_admin_page()
        self.check_page_title(self.data_admin_config.get('PAGE_TITLE'))
        self.check_page_contains_ids(self.data_admin_config.get('ADMIN_LINKS'))

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
        self.wait_until_element_appear('site-name', 10)
        self.check_page_title(self.data_management_config.get('PAGE_TITLE'))
