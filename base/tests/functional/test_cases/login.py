from django.test import tag

from base.tests.factories.user import UserFactory
from base.tests.functional.models.base_model import FunctionalTestCase


@tag('selenium')
class LoginTestCase(FunctionalTestCase):

    def setUp(self):
        super(LoginTestCase, self).setUp()
        self.valid_user = UserFactory()

    def test_login_page(self):
        self.openUrl('login')
        self.check_page_title('Login')

    def test_valid_login(self):
        self.login(self.valid_user.username, 'password123')
        self.check_page_title('Dashbord')

    def test_invalid_login(self):
        self.login(self.valid_user.username, 'wrong_password')




