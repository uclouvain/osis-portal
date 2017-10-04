##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2016 Université catholique de Louvain (http://www.uclouvain.be)
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
import json
from mock import patch

from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import Group, Permission
from django.core.urlresolvers import reverse
from django.test import TestCase, Client

from base.tests.factories.person import PersonFactory
from base.tests.factories.student import StudentFactory
from attestation.views import main as v_main


OK = 200
BAD_REQUEST = 400
ACCESS_DENIED = 401
FILE_NOT_FOUND = 404
METHOD_NOT_ALLOWED = 405


class HomeTest(TestCase):
    def setUp(self):
        self.url = reverse('attestation_home')
        self.client = Client()
        self.person = PersonFactory()

        students_group = Group.objects.create(name='students')
        self.permission = Permission.objects.get(codename="is_student")
        students_group.permissions.add(self.permission)

    def test_without_being_logged(self):
        response = self.client.get(self.url)
        self.assertRedirects(response, '/login/?next={}'.format(self.url))

    def test_with_user_not_a_student(self):
        self.client.force_login(self.person.user)
        response = self.client.get(self.url, follow=True)

        self.assertTemplateUsed(response, "access_denied.html")
        self.assertEqual(response.status_code, ACCESS_DENIED)

    def test_with_multiple_students_assigned_same_person(self):
        StudentFactory(person=self.person)
        StudentFactory(person=self.person)

        self.client.force_login(self.person.user)
        response = self.client.get(self.url, follow=True)

        self.assertTemplateUsed(response, "dashboard.html")

        messages = list(response.context['messages'])

        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].tags, 'error')
        self.assertEqual(messages[0].message, _('error_multiple_registration_id'))

    @patch('attestation.queues.student_attestation_status.fetch_json_attestation_statuses', side_effect=lambda x: None)
    def test_when_not_receive_attestation_statuses(self, mock_fetch_json_attestation_statuses):
        a_student = StudentFactory(person=self.person)

        self.client.force_login(self.person.user)
        response = self.client.get(self.url, follow=True)

        self.assertTrue(mock_fetch_json_attestation_statuses.called)
        self.assertEqual(response.status_code, OK)
        self.assertTemplateUsed(response, 'attestation_home_student.html')

        self.assertEqual(response.context['student'], a_student)

        self.assertFalse(response.context['attestation_statuses'])
        self.assertFalse(response.context['academic_year'])
        self.assertFalse(response.context['formated_academic_year'])
        self.assertFalse(response.context['available'])

    @patch('attestation.queues.student_attestation_status.fetch_json_attestation_statuses',
           side_effect=lambda x: {'academicYear': 2015, 'available': False, 'attestationStatuses': []})
    def test_when_receive_attestation_statuses(self, mock_fetch_json_attestation_statuses):
        a_student = StudentFactory(person=self.person)

        self.client.force_login(self.person.user)
        response = self.client.get(self.url, follow=True)

        self.assertTrue(mock_fetch_json_attestation_statuses.called)
        self.assertEqual(response.status_code, OK)
        self.assertTemplateUsed(response, 'attestation_home_student.html')

        self.assertEqual(response.context['student'], a_student)
        self.assertEqual(response.context['academic_year'], 2015)
        self.assertEqual(response.context['formated_academic_year'], "2015 - 2016")

        self.assertFalse(response.context['attestation_statuses'])
        self.assertFalse(response.context['available'])

    def test_when_no_student_find_by_user(self):
        self.person.user.user_permissions.add(self.permission)

        self.client.force_login(self.person.user)
        response = self.client.get(self.url, follow=True)

        self.assertEqual(response.status_code, OK)
        self.assertTemplateUsed(response, 'attestation_home_student.html')

        self.assertFalse(response.context['attestation_statuses'])
        self.assertFalse(response.context['student'])
        self.assertFalse(response.context['academic_year'])
        self.assertFalse(response.context['formated_academic_year'])
        self.assertFalse(response.context['available'])


class TestRegistrationIdMessage(TestCase):

    def test_generate_message_with_registration_id(self):
        given_json_message = v_main._make_registration_json_message('1111111')
        expected_json_message = json.loads('{"registration_id" : "1111111"}')
        self.assertJSONEqual(given_json_message, expected_json_message)

    def test_generate_message_without_registration_id(self):
        given_json_message = v_main._make_registration_json_message(None)
        self.assertIsNone(given_json_message)

