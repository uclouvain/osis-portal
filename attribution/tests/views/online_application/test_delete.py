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
import uuid

import mock
from django.http import HttpResponseNotAllowed
from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from attribution.tests.views.online_application.common import OnlineApplicationContextTestMixin
from base.tests.factories.person import PersonFactory
from base.tests.factories.tutor import TutorFactory
from base.tests.factories.user import UserFactory


class TestDeleteApplicationView(OnlineApplicationContextTestMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.url = reverse('delete_application', kwargs={'application_uuid': uuid.uuid4()})
        cls.tutor = TutorFactory(person__global_id='578945612')
        cls.person = PersonFactory(global_id="9999999")

    def setUp(self):
        self.open_application_course_calendar()

        # Create mock ApplicationService
        self.delete_application_mocked = mock.Mock(return_value=[])
        self.application_service_patcher = mock.patch.multiple(
            'attribution.services.application.ApplicationService',
            delete_application=self.delete_application_mocked
        )
        self.application_service_patcher.start()
        self.addCleanup(self.application_service_patcher.stop)

        self.client.force_login(self.person.user)

    def test_case_user_not_logged(self):
        self.client.logout()

        response = self.client.post(self.url, follow=False)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_case_calendar_not_opened_assert_redirection_to_outside_encoding_period(self):
        self.calendar.start_date = datetime.date.today() + datetime.timedelta(days=5)
        self.calendar.is_open = False

        expected_redirect = reverse('outside_applications_period')
        response = self.client.post(self.url, follow=False)
        self.assertRedirects(response, expected_redirect, fetch_redirect_response=False)

    def test_assert_methods_not_allowed(self):
        methods_not_allowed = ['get']

        for method in methods_not_allowed:
            response = getattr(self.client, method)(self.url)
            self.assertEqual(response.status_code, HttpResponseNotAllowed.status_code)

    def test_post_assert_call_application_service(self):
        response = self.client.post(self.url, data={}, follow=False)

        expected_redirect = reverse('applications_overview')
        self.assertRedirects(response, expected_redirect, fetch_redirect_response=False)

        self.assertTrue(self.delete_application_mocked.called)
