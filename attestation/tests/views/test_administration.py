##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2022 Université catholique de Louvain (http://www.uclouvain.be)
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
from django.contrib.auth.models import Group, Permission
from django.test import TestCase
from django.urls import reverse
from mock import patch
from osis_reference_sdk.model.academic_calendar import AcademicCalendar
from osis_reference_sdk.model.paginated_academic_calendars import PaginatedAcademicCalendars

from base.forms.base_forms import RegistrationIdForm
from base.tests.factories.person import PersonFactory
from base.tests.factories.student import StudentFactory

STUDENT_REGISTRATION_ID = "70531800"


class AttestationAdministrationTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.url = reverse('attestation_administration')
        cls.person = PersonFactory()

        cls.permission = Permission.objects.get(codename="is_faculty_administrator")
        cls.person.user.user_permissions.add(cls.permission)

    def setUp(self):
        self.client.force_login(self.person.user)

    def test_without_being_logged(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertRedirects(response, f'/login/?next={self.url}')

    def test_when_user_is_not_a_faculty_administrator(self):
        a_person = PersonFactory()
        self.client.force_login(a_person.user)
        response = self.client.get(self.url, follow=True)

        self.assertTemplateUsed(response, "access_denied.html")
        self.assertEqual(response.status_code, 403)

    def test_when_faculty_administrator(self):
        response = self.client.get(self.url, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "admin/attestation_administration.html")


class SelectStudentAttestationTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.url = reverse('attestation_admin_select_student')
        cls.person = PersonFactory()

        cls.permission = Permission.objects.get(codename="is_faculty_administrator")
        cls.person.user.user_permissions.add(cls.permission)

        Group.objects.create(name='students')

    def setUp(self):
        self.client.force_login(self.person.user)

        self.academic_calendar_row = AcademicCalendar(**{
            'reference': 'REFERENCE',
            'title': 'TITLE',
            'data_year': 2021,
            'start_date': datetime.date.today(),
            'end_date': datetime.date.today()
        })
        self.academic_calendar_list_patcher = mock.patch(
            "reference.services.academic_calendar.AcademicCalendarService.get_academic_calendar_list",
            return_value=PaginatedAcademicCalendars(**{'results': [self.academic_calendar_row]})
        )
        self.mocked_academic_calendar_list = self.academic_calendar_list_patcher.start()
        self.addCleanup(self.academic_calendar_list_patcher.stop)

    def test_without_being_logged(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertRedirects(response, f'/login/?next={self.url}')

    def test_when_user_is_not_a_faculty_administrator(self):
        a_person = PersonFactory()
        self.client.force_login(a_person.user)
        response = self.client.get(self.url, follow=True)

        self.assertTemplateUsed(response, "access_denied.html")
        self.assertEqual(response.status_code, 403)

    def test_get_request(self):
        response = self.client.get(self.url, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "admin/attestation_administration.html")

        self.assertIsInstance(response.context['form'], RegistrationIdForm)

    def test_invalid_post_request(self):
        response = self.client.post(self.url, data={'registration_id': STUDENT_REGISTRATION_ID}, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "admin/attestation_administration.html")
        # Message valided in base test
        self.assertEqual(len(response.context['form'].errors), 1)

    @patch('attestation.queues.student_attestation_status.fetch_json_attestation_statuses', side_effect=lambda x: None)
    def test_valid_post_request_but_no_attestation(self, mock_fetch_json_attestation_statuses):
        a_student = StudentFactory(registration_id=STUDENT_REGISTRATION_ID)
        response = self.client.post(self.url, data={'registration_id': STUDENT_REGISTRATION_ID}, follow=True)

        self.assertTrue(mock_fetch_json_attestation_statuses.called)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "attestation_home_admin.html")

        self.assertEqual(response.context['student'], a_student)

        self.assertFalse(response.context['attestations'])
        self.assertFalse(response.context['current_year'])

    @patch('attestation.queues.student_attestation_status.fetch_json_attestation_statuses',
           side_effect=lambda x: {'current_year': 2015, 'attestations': [],
                                  'registration_id': STUDENT_REGISTRATION_ID})
    def test_valid_post_request(self, mock_fetch_json_attestation_statuses):
        a_student = StudentFactory(registration_id=STUDENT_REGISTRATION_ID)
        response = self.client.post(self.url, data={'registration_id': STUDENT_REGISTRATION_ID}, follow=True)

        self.assertTrue(mock_fetch_json_attestation_statuses.called)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "attestation_home_admin.html")

        self.assertEqual(response.context['student'], a_student)
        self.assertEqual(response.context['current_year'], 2015)

        self.assertFalse(response.context['attestations'])
