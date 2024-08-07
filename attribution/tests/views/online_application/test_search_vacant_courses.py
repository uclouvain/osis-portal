##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2023 Université catholique de Louvain (http://www.uclouvain.be)
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

from attribution.forms.application import VacantAttributionFilterForm
from attribution.tests.views.online_application.common import OnlineApplicationContextTestMixin
from base.tests.factories.person import PersonFactory


class TestSearchVacantCourseView(OnlineApplicationContextTestMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.url = reverse('search_vacant_courses')
        cls.person = PersonFactory(global_id="9999999")

    def setUp(self):
        self.open_application_course_calendar()

        # Create mock ApplicationService
        self.search_vacant_courses_mocked = mock.Mock(return_value=[])
        self.application_service_patcher = mock.patch.multiple(
            'attribution.services.application.ApplicationService',
            search_vacant_courses=self.search_vacant_courses_mocked
        )
        self.application_service_patcher.start()
        self.addCleanup(self.application_service_patcher.stop)

        self.client.force_login(self.person.user)

    def test_case_user_not_logged(self):
        self.client.logout()

        response = self.client.get(self.url, follow=False)
        self.assertEqual(response.status_code, 302)

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
        "HELP_BUTTON_URL": "https://dummy-url.com"
    })
    def test_get_assert_context(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, HttpResponse.status_code)
        self.assertEqual(response.context['a_person'], self.person)
        self.assertIsInstance(response.context['form'], VacantAttributionFilterForm)
        self.assertEqual(response.context['help_button_url'], "https://dummy-url.com")

    def test_get_with_queryparams_assert_call_application_service(self):
        query_params = {'learning_container_acronym': 'LDR'}

        response = self.client.get(self.url, data=query_params)
        self.assertEqual(response.status_code, HttpResponse.status_code)

        self.assertTrue(self.search_vacant_courses_mocked.called)
