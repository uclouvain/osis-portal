from django.test import tag

from base.tests.factories.user import UserFactory
from base.tests.functional.models.base_model import FunctionalTestCase
from django.utils.translation import ugettext as _

from base.tests.functional.models.user_type import StudentMixin


class BasicLoginTestCase(FunctionalTestCase):

    def setUp(self):
        super(BasicLoginTestCase, self).setUp()
        self.valid_user = UserFactory()

    def test_login_page(self):
        """
        As a not connected user
        I should see the login page
        """
        self.openUrl('login')
        self.check_page_title('Login')

    def test_valid_login(self):
        """
        As a registered user with valid password
        I should be able to connect
        """
        self.login(self.valid_user.username, 'password123')
        self.check_page_title(self.config.get('DASHBOARD').get('PAGE_TITLE'))

    def test_invalid_login(self):
        """
        As a registered user with wrong password
        I scould not be able to connect
        """
        self.login(self.valid_user.username, 'wrong_password')
        string = _('msg_error_username_password_not_matching')
        self.check_page_contains_string(string)


class StudentLoginTestCase(FunctionalTestCase, StudentMixin):

    @classmethod
    def setUpClass(cls):
        super(StudentLoginTestCase, cls).setUpClass()
        cls.dashboard_config = cls.config.get('DASHBOARD')

    def setUp(self):
        super(StudentLoginTestCase, self).setUp()
        self.student = self.create_student()

    def test_student_login(self):
        """
        As a student
         - I should be able to connect
         - I should see the student links
         - I should not see the tutor links
         - I should no see the admin links
        """
        self.login(self.student.person.user.username, 'password123')
        self.check_page_contains_ids(self.dashboard_config.get('STUDENT_LINKS'))
        self.check_page_not_contains_ids(self.dashboard_config.get('TUTOR_LINKS'))
        self.check_page_not_contains_ids(self.dashboard_config.get('ADMIN_LINKS'))






