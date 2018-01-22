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
from django.test import TestCase, Client

import base.tests.models.test_student
from django.contrib.auth.models import User, Permission
from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist
from internship.models import internship_student_information as mdl_student_information
from internship.tests.models import test_internship_student_information
from internship.tests.factories.cohort import CohortFactory

class TestResumeUrl(TestCase):
    def setUp(self):
        self.c = Client()
        self.student = base.tests.models.test_student.create_student("45451298")
        self.user = User.objects.create_user('user', 'user@test.com', 'userpass')
        self.student.person.user = self.user
        self.student.person.save()
        self.cohort = CohortFactory()
        self.student_information = test_internship_student_information.create_student_information(self.user, self.cohort, self.student.person)
        add_permission(self.student.person.user, "can_access_internship")

    def test_can_access_student_resume(self):
        url = reverse("student_resume", kwargs={'cohort_id': self.cohort.id})
        response = self.c.get(url)
        self.assertEqual(response.status_code, 302)

        self.c.force_login(self.user)
        response = self.c.get(url)
        self.assertEqual(response.status_code, 200)

    def test_can_access_student_info_modification(self):
        url = reverse("internship_student_edit", kwargs={'cohort_id': self.cohort.id})
        response = self.c.get(url)
        self.assertEqual(response.status_code, 302)

        self.c.force_login(self.user)
        response = self.c.get(url)
        self.assertEqual(response.status_code, 200)


class TestEditStudentInformation(TestCase):
    def setUp(self):
        self.student = base.tests.models.test_student.create_student("45451298")
        self.user = User.objects.create_user('user', 'user@test.com', 'userpass')
        self.student.person.user = self.user
        self.student.person.save()
        self.cohort = CohortFactory()
        self.student_information = test_internship_student_information.create_student_information(self.user, self.cohort, self.student.person)
        add_permission(self.student.person.user, "can_access_internship")
        self.c = Client()
        self.c.force_login(self.user)

        self.url = reverse("internship_student_edit", kwargs={'cohort_id': self.cohort.id})

        self.data = {
            "location": "location",
            "postal_code": "postal",
            "city": "city",
            "country": "country",
            "email": "test@test.com",
            "phone_mobile": "0236478987",
            "contest": "GENERALIST",
        }

    def test_information_save(self):
        self.c.post(self.url, data=self.data)
        try:
            student_information = mdl_student_information.find_by_user_and_cohort(self.user, cohort=self.cohort)
        except ObjectDoesNotExist:
            self.fail()

        self.assertEqual(student_information.location, self.data["location"])
        self.assertEqual(student_information.postal_code, self.data["postal_code"])
        self.assertEqual(student_information.city, self.data["city"])
        self.assertEqual(student_information.country, self.data["country"])
        self.assertEqual(student_information.email, self.data["email"])
        self.assertEqual(student_information.phone_mobile, self.data["phone_mobile"])
        self.assertEqual(student_information.contest, self.data["contest"])


def add_permission(user, codename):
    perm = get_permission(codename)
    user.user_permissions.add(perm)


def get_permission(codename):
    return Permission.objects.get(codename=codename)
