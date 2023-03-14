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
from django.http import HttpResponse
from django.test import TestCase, override_settings
from django.urls import reverse
from osis_attribution_sdk.model.application import Application
from osis_attribution_sdk.model.vacant_course import VacantCourse
from osis_attribution_sdk.model.vacant_declaration_type_enum import VacantDeclarationTypeEnum
from rest_framework import status

from attribution.tests.views.online_application.common import OnlineApplicationContextTestMixin
from base.tests.factories.person import PersonFactory
from base.tests.factories.tutor import TutorFactory
from base.tests.factories.user import UserFactory


class TestUpdateApplicationView(OnlineApplicationContextTestMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.application_uuid = uuid.uuid4()
        cls.url = reverse('update_application', kwargs={'application_uuid': cls.application_uuid})
        cls.person = PersonFactory(global_id='9999999')

    def setUp(self):
        self.open_application_course_calendar()

        # Create mock ApplicationService
        self.update_application_mocked = mock.Mock(return_value=None)
        self.get_vacant_course_mocked = mock.Mock(
            return_value=VacantCourse(
                code='LDROI1200',
                year=2020,
                lecturing_volume_total='20.0',
                practical_volume_total='10.0',
                lecturing_volume_available='10.0',
                practical_volume_available='10.0',
                title='Introduction au droit',
                vacant_declaration_type=VacantDeclarationTypeEnum("RESEVED_FOR_INTERNS"),
                vacant_declaration_type_text='Reserved for interns',
                is_in_team=False,
                allocation_entity='DRT',
            )
        )
        self.get_application_mocked = mock.Mock(
            return_value=Application(
                uuid=str(self.application_uuid),
                code='LDROI1200',
                year=2020,
                lecturing_volume='10.0',
                practical_volume='5.0',
                remark='',
                course_summary='',
            )
        )

        self.application_service_patcher = mock.patch.multiple(
            'attribution.services.application.ApplicationService',
            update_application=self.update_application_mocked,
            get_application=self.get_application_mocked,
            get_vacant_course=self.get_vacant_course_mocked
        )
        self.application_service_patcher.start()
        self.addCleanup(self.application_service_patcher.stop)

        self.client.force_login(self.person.user)

    def test_case_user_not_logged(self):
        self.client.logout()

        response = self.client.get(self.url, follow=False)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

    def test_case_calendar_not_opened_assert_redirection_to_outside_encoding_period(self):
        self.calendar.start_date = datetime.date.today() + datetime.timedelta(days=5)
        self.calendar.is_open = False

        expected_redirect = reverse('outside_applications_period')
        response = self.client.get(self.url, follow=False)
        self.assertRedirects(response, expected_redirect, fetch_redirect_response=False)

    @override_settings(ATTRIBUTION_CONFIG={
        "HELP_BUTTON_URL": "https://dummy-url.com"
    })
    def test_get_method_assert_context(self):
        response = self.client.get(self.url, data={}, follow=False)

        self.assertEqual(response.status_code, HttpResponse.status_code)
        self.assertEqual(response.context['a_person'], self.person)
        self.assertEqual(response.context['save_url'], self.url)
        self.assertEqual(response.context['cancel_url'], reverse('applications_overview'))
        self.assertEqual(response.context['help_button_url'], "https://dummy-url.com")

    def test_post_assert_call_application_service(self):
        response = self.client.post(self.url, data={}, follow=False)

        expected_redirect = reverse('applications_overview')
        self.assertRedirects(response, expected_redirect, fetch_redirect_response=False)

        self.assertTrue(self.update_application_mocked.called)
