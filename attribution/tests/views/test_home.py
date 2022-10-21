from django.test import TestCase
from django.urls import reverse

from base.tests.factories.user import UserFactory


class HomeAttributionTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory()
        cls.url = reverse('attribution_home')

    def setUp(self) -> None:
        self.client.force_login(self.user)

    def test_case_user_not_logged(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertRedirects(response, f'/login/?next={self.url}')

    def test_assert_redirect_to_tutor_charge_view(self):
        expected_redirection = reverse('tutor_charge')

        response = self.client.get(self.url)
        self.assertRedirects(response, expected_redirection, fetch_redirect_response=False)
