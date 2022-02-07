##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2021 Université catholique de Louvain (http://www.uclouvain.be)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
import datetime

import mock
from django.http import HttpResponseNotAllowed, HttpResponse
from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework import status

from attribution.tests.views.online_application.common import OnlineApplicationContextTestMixin
from base.templatetags.academic_year_display import display_as_academic_year
from base.tests.factories.tutor import TutorFactory
from base.tests.factories.user import UserFactory


class TestApplicationOverviewView(OnlineApplicationContextTestMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.url = reverse('applications_overview')
        cls.tutor = TutorFactory(person__global_id='578945612')

    def setUp(self) -> None:
        self.open_application_course_calendar()
        self.add_can_access_application_permission_to_user(self.tutor.person.user)

        # Mock application service
        self.get_applications_mocked = mock.Mock(return_value=[])
        self.get_attribution_about_to_expires_mocked = mock.Mock(return_value=[])
        self.get_my_charge_summary_mocked = mock.Mock(return_value=[])
        self.application_service_patcher = mock.patch.multiple(
            'attribution.services.application.ApplicationService',
            get_applications=self.get_applications_mocked,
            get_attribution_about_to_expires=self.get_attribution_about_to_expires_mocked,
            get_my_charge_summary=self.get_my_charge_summary_mocked

        )
        self.application_service_patcher.start()
        self.addCleanup(self.application_service_patcher.stop)

        self.client.force_login(self.tutor.person.user)

    def test_case_user_not_logged(self):
        self.client.logout()

        response = self.client.get(self.url, follow=False)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_case_user_without_permission(self):
        self.client.force_login(UserFactory())

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_case_calendar_not_opened_assert_redirection_to_outside_encoding_period(self):
        self.calendar.start_date = datetime.date.today() + datetime.timedelta(days=5)
        self.calendar.is_open = False

        expected_redirect = reverse('outside_applications_period')
        response = self.client.get(self.url, follow=False)
        self.assertRedirects(response, expected_redirect, fetch_redirect_response=False)  # Redirection

    def test_assert_methods_not_allowed(self):
        methods_not_allowed = ['post']

        for method in methods_not_allowed:
            response = getattr(self.client, method)(self.url)
            self.assertEqual(response.status_code, HttpResponseNotAllowed.status_code)

    @override_settings(ATTRIBUTION_CONFIG={
        "HELP_BUTTON_URL": "https://dummy-url.com",
        "CATALOG_URL": "https://catalogue_url.com"
    })
    def test_get_method_assert_context(self):
        response = self.client.get(self.url, follow=False)

        self.assertEqual(response.status_code, HttpResponse.status_code)
        self.assertEqual(response.context['a_tutor'], self.tutor)
        self.assertEqual(response.context['application_course_calendar'], self.calendar)
        self.assertEqual(
            response.context['application_academic_year'],
            display_as_academic_year(self.calendar.authorized_target_year)
        )
        self.assertEqual(
            response.context['previous_academic_year'],
            display_as_academic_year(self.calendar.authorized_target_year - 1)
        )
        self.assertEqual(response.context['help_button_url'], "https://dummy-url.com")
        self.assertEqual(response.context['catalog_url'], "https://catalogue_url.com")

        self.assertTrue("attributions_about_to_expire" in response.context)
        self.assertTrue("attributions" in response.context)
        self.assertTrue("tot_lecturing" in response.context)
        self.assertTrue("tot_practical" in response.context)
        self.assertTrue("applications" in response.context)

    def test_get_method_called_multiple_service_to_fetch_data(self):
        self.client.get(self.url, follow=False)

        # Application Service
        self.assertTrue(self.get_applications_mocked.called)
        self.assertTrue(self.get_attribution_about_to_expires_mocked.called)
        self.assertTrue(self.get_my_charge_summary_mocked.called)
