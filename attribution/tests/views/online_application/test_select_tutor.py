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
import mock
from django.contrib.auth.models import Permission
from django.test import TestCase
from django.urls import reverse

from base.tests.factories.person import PersonFactory
from base.tests.factories.tutor import TutorFactory


class TestSelectTutor(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.url = reverse("attribution_applications")
        cls.person = PersonFactory()
        permission = Permission.objects.get(codename="is_faculty_administrator")
        cls.person.user.user_permissions.add(permission)

    def setUp(self):
        self.client.force_login(self.person.user)

    def test_is_not_faculty_admin(self):
        self.client.force_login(PersonFactory().user)
        response = self.client.get(self.url, follow=True)

        self.assertEqual(response.status_code, 401)
        self.assertTemplateUsed(response, 'access_denied.html')

    def test_is_faculty_manager(self):
        response = self.client.get(self.url, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "admin/applications_administration.html")

    @mock.patch('attribution.views.online_application.overview.ApplicationOverviewView.application_course_calendar')
    @mock.patch('attribution.utils.permission.is_online_application_opened', return_value=True)
    def test_select_tutor(self, mock_calendar, mock_course_calendar):
        # Mock application service
        get_applications_mocked = mock.Mock(return_value=[])
        get_attribution_about_to_expires_mocked = mock.Mock(return_value=[])
        get_my_charge_summary_mocked = mock.Mock(return_value=[])
        application_service_patcher = mock.patch.multiple(
            'attribution.services.application.ApplicationService',
            get_applications=get_applications_mocked,
            get_attribution_about_to_expires=get_attribution_about_to_expires_mocked,
            get_my_charge_summary=get_my_charge_summary_mocked

        )
        application_service_patcher.start()

        tutor = TutorFactory()
        response = self.client.post(self.url, data={'global_id': tutor.person.global_id})
        self.assertEqual(response.status_code, 302)
        expected_url = reverse('visualize_tutor_applications', kwargs={'global_id': tutor.person.global_id})
        self.assertRedirects(response, expected_url)

        application_service_patcher.stop()
