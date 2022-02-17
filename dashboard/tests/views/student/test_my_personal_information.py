##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2018 Université catholique de Louvain (http://www.uclouvain.be)
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
from unittest.mock import patch

from django.contrib.auth.models import Group, Permission
from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from base.tests.factories.person import PersonFactory
from base.tests.factories.student import StudentFactory


class TestMyPersonalInformation(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.url = reverse("student_id_data_home")

    def test_not_student(self):
        person = PersonFactory()
        self.client.logout()
        self.client.force_login(person.user)

        response = self.client.get(self.url, follow=True)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTemplateUsed(response, 'access_denied.html')

    @patch('dashboard.business.id_data.get_student_id_data')
    def test_is_student(self, mock_client_call):
        mock_client_call.return_value = \
            json.loads(load_json_file("dashboard/tests/resources/student_id_data.json"))
        self.client.logout()
        students_group = Group.objects.create(name="students")
        permission = Permission.objects.get(codename="is_student")
        students_group.permissions.add(permission)
        student = StudentFactory()
        self.client.force_login(student.person.user)

        response = self.client.get(self.url, follow=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTemplateUsed(response, 'student/id_data_home.html')


class TestMyPersonalInformationAdmin(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.url = reverse("student_id_data_administration")

    def setUp(self):
        self.person = PersonFactory()

    def test_is_not_faculty_admin(self):
        self.client.logout()
        self.client.force_login(self.person.user)

        response = self.client.get(self.url, follow=True)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTemplateUsed(response, 'access_denied.html')

    def test_is_faculty_manager(self):
        self.client.logout()
        permission = Permission.objects.get(codename="is_faculty_administrator")
        self.person.user.user_permissions.add(permission)
        self.client.force_login(self.person.user)

        response = self.client.get(self.url, follow=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTemplateUsed(response, 'admin/student_id_data_administration.html')

    @patch('dashboard.business.id_data.get_student_id_data')
    def test_select_student(self, mock_client_call):
        mock_client_call.return_value = \
            json.loads(load_json_file("dashboard/tests/resources/student_id_data.json"))
        self.client.logout()
        permission = Permission.objects.get(codename="is_faculty_administrator")
        self.person.user.user_permissions.add(permission)
        self.client.force_login(self.person.user)
        student = StudentFactory()
        response = self.client.post(self.url, data={'registration_id': student.registration_id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTemplateUsed(response, 'admin/student_id_data.html')


def load_json_file(json_path):
    with open(json_path) as json_file:
        return json_file.read()
