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
from django.contrib.auth.models import Permission
from django.test import TestCase
from django.urls import reverse

from base.tests.factories.student import StudentFactory
from internship.tests.factories.cohort import CohortFactory
from internship.tests.models import test_internship_student_information


class TestResumeUrl(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.student = StudentFactory()
        cls.user = cls.student.person.user
        cls.cohort = CohortFactory()
        cls.student_information = test_internship_student_information.create_student_information(cls.user,
                                                                                                 cls.cohort,
                                                                                                 cls.student.person)
        perm = Permission.objects.get(codename="can_access_internship")
        cls.user.user_permissions.add(perm)

    def test_can_access_student_resume(self):
        url = reverse("student_resume", kwargs={'cohort_id': self.cohort.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

        self.client.force_login(self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
