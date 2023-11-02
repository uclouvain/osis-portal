##############################################################################
#
# OSIS stands for Open Student Information System. It's an application
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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
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

from base.tests.factories.student import StudentFactory
from base.tests.factories.user import UserFactory
from internship.tests.services.test_api_client import MockAPI


class TestHospitalUrl(TestCase):

    def setUp(self):
        self.api_patcher = mock.patch(
            "internship.services.internship.InternshipAPIClient.__new__",
            return_value=MockAPI
        )
        self.client.force_login(self.user)
        self.api_patcher.start()
        self.addCleanup(self.api_patcher.stop)

    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory()
        cls.student = StudentFactory(registration_id="45451298", person__user=cls.user)

        perm = Permission.objects.get(codename="can_access_internship", content_type__model='internshipoffer')
        cls.student.person.user.user_permissions.add(perm)

    def test_can_access_hospital_list(self):
        home_url = reverse("hospitals_list", kwargs={'cohort_id': "cohort"})
        response = self.client.get(home_url)
        self.assertEqual(response.status_code, 200)
