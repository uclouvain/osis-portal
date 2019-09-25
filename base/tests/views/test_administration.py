##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2018 Université catholique de Louvain (http://www.uclouvain.be)
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
from unittest.mock import patch

from django.test import TestCase, override_settings
from django.conf import settings
from django.urls import reverse
from django.contrib.auth.models import Permission
from django.http.response import HttpResponse

from base.tests.factories.person import PersonFactory


HTTP_ACCESS_DENIED = 401


class TestData(TestCase):
    def setUp(self):
        self.person = PersonFactory()
        self.person.user.is_staff = True
        self.person.user.save()

        self.admin_perm = Permission.objects.get(codename="is_administrator")
        self.person.user.user_permissions.add(self.admin_perm)

        self.url = reverse("data")
        self.client.force_login(self.person.user)

    def test_user_not_logged(self):
        self.client.logout()
        response = self.client.get(self.url)

        self.assertRedirects(response, '/login/?next={}'.format(self.url))


    def test_user_is_not_staff(self):
        self.person.user.is_staff = False
        self.person.user.save()

        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, HTTP_ACCESS_DENIED)
        self.assertTemplateUsed(response, "access_denied.html")

    def test_user_is_not_administrator(self):
        self.person.user.user_permissions.remove(self.admin_perm)

        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, HTTP_ACCESS_DENIED)
        self.assertTemplateUsed(response, "access_denied.html")

    @override_settings(ENABLE_SQL_DATA_MANAGEMENT=False)
    def test_with_sql_data_management_disabled(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "admin/data.html")
        self.assertEqual(response.status_code, HttpResponse.status_code)
        self.assertEqual(response.context["sql_data_management_enabled"], False)

    @override_settings()
    def test_with_sql_data_management_setting_non_existent(self):
        del settings.ENABLE_SQL_DATA_MANAGEMENT

        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "admin/data.html")
        self.assertEqual(response.status_code, HttpResponse.status_code)
        self.assertEqual(response.context["sql_data_management_enabled"], False)

    @override_settings(ENABLE_SQL_DATA_MANAGEMENT=True)
    def test_with_sql_data_management_enabled(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "admin/data.html")
        self.assertEqual(response.status_code, HttpResponse.status_code)
        self.assertEqual(response.context["sql_data_management_enabled"], True)



class TestDataMaintenance(TestCase):
    def setUp(self):
        self.person = PersonFactory()
        self.person.user.is_staff = True
        self.person.user.save()

        self.admin_perm = Permission.objects.get(codename="is_administrator")
        self.person.user.user_permissions.add(self.admin_perm)

        self.url = reverse("data_maintenance")
        self.client.force_login(self.person.user)

    def test_user_not_logged(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertRedirects(response, '/login/?next={}'.format(self.url))


    def test_user_is_not_staff(self):
        self.person.user.is_staff = False
        self.person.user.save()

        response = self.client.post(self.url, follow=True)
        self.assertEqual(response.status_code, HTTP_ACCESS_DENIED)
        self.assertTemplateUsed(response, "access_denied.html")

    def test_user_is_not_administrator(self):
        self.person.user.user_permissions.remove(self.admin_perm)

        response = self.client.post(self.url, follow=True)
        self.assertEqual(response.status_code, HTTP_ACCESS_DENIED)
        self.assertTemplateUsed(response, "access_denied.html")

    @override_settings(ENABLE_SQL_DATA_MANAGEMENT=False)
    def test_with_sql_data_management_disabled(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, HTTP_ACCESS_DENIED)
        self.assertTemplateUsed(response, "access_denied.html")

    @override_settings()
    def test_with_sql_data_management_setting_non_existent(self):
        del settings.ENABLE_SQL_DATA_MANAGEMENT
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, HTTP_ACCESS_DENIED)
        self.assertTemplateUsed(response, "access_denied.html")

    @override_settings(ENABLE_SQL_DATA_MANAGEMENT=True)
    @override_settings(FORBIDDEN_SQL_KEYWORDS=['alter',  'create'])
    def test_with_forbidden_keyword(self):
        response = self.client.post(self.url, data={"sql_command": "CREATE TABLE TEMP;"})
        self.assertEqual(response.status_code, HTTP_ACCESS_DENIED)
        self.assertTemplateUsed(response, "access_denied.html")

    @override_settings(ENABLE_SQL_DATA_MANAGEMENT=True)
    @override_settings(FORBIDDEN_SQL_KEYWORDS=['update'])
    @override_settings(SQL_DATA_MANAGEMENT_READONLY=True)
    @patch("osis_common.utils.native.execute", side_effect=lambda command: [])
    def test_with_valid_query(self, mock_execute_query):
        sql_command = "SELECT * FROM TEMP;"

        response = self.client.post(self.url, data={"sql_command": sql_command})
        self.assertTemplateUsed(response, "admin/data_maintenance.html")
        self.assertEqual(response.status_code, HttpResponse.status_code)
        self.assertTrue(mock_execute_query.called)
        expected_context = {
            'section': 'data_maintenance',
            'sql_command': sql_command,
            'results': [],
            'sql_readonly': True,
            'forbidden_sql_keywords': ['update']
        }

        for key, value in expected_context.items():
            self.assertEqual(response.context[key], value)



