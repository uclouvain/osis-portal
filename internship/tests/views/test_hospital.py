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
from internship.tests.models import test_organization_address, test_organization
from internship.views import hospital


class TestHospitalUrl(TestCase):
    def setUp(self):
        self.c = Client()
        self.student = base.tests.models.test_student.create_student("45451298")
        self.user = User.objects.create_user('user', 'user@test.com', 'userpass')
        self.student.person.user = self.user
        self.student.person.save()
        add_permission(self.student.person.user, "is_student")

    def test_can_access_hospital_list(self):
        home_url = reverse("hospitals_list")
        response = self.c.get(home_url)
        self.assertEqual(response.status_code, 302)

        self.c.force_login(self.user)
        response = self.c.get(home_url)
        self.assertEqual(response.status_code, 200)


class TestGetHospitals(TestCase):
    def setUp(self):
        self.organization_1 = test_organization.create_organization()
        self.organization_address_1 = \
            test_organization_address.create_organization_address(self.organization_1, city="city1")
        self.organization_2 = test_organization.create_organization(reference='02')
        self.organization_address_2 = \
            test_organization_address.create_organization_address(self.organization_2, city="city2")
        self.organization_3 = test_organization.create_organization(name="OSAS", reference='03')
        self.organization_address_3 = \
            test_organization_address.create_organization_address(self.organization_3, city="city1")

    def test_with_no_criteria(self):
        hospitals = hospital.get_hospitals()
        self.assertEqual(len(hospitals), 3)
        self.assertIn((self.organization_1, self.organization_address_1), hospitals)
        self.assertIn((self.organization_2, self.organization_address_2), hospitals)
        self.assertIn((self.organization_3, self.organization_address_3), hospitals)

    def test_with_name(self):
        hospitals = hospital.get_hospitals(name="OSIS")
        self.assertEqual(len(hospitals), 2)
        self.assertIn((self.organization_1, self.organization_address_1), hospitals)
        self.assertIn((self.organization_2, self.organization_address_2), hospitals)

    def test_with_city(self):
        hospitals = hospital.get_hospitals(city="city1")
        self.assertEqual(len(hospitals), 2)
        self.assertIn((self.organization_1, self.organization_address_1), hospitals)
        self.assertIn((self.organization_3, self.organization_address_3), hospitals)

    def test_with_name_and_city(self):
        hospitals = hospital.get_hospitals(name="OSIS", city="city2")
        self.assertEqual(len(hospitals), 1)
        self.assertIn((self.organization_2, self.organization_address_2), hospitals)

    def test_with_organization_without_address(self):
        organization = test_organization.create_organization(name="NO_ADDRESS")
        hospitals = hospital.get_hospitals(name="NO_ADDRESS")
        self.assertEqual(len(hospitals), 1)
        self.assertIn((organization, None), hospitals)

        hospitals = hospital.get_hospitals(name="NO_ADDRESS", city="city")
        self.assertEqual(len(hospitals), 0)


def add_permission(user, codename):
    perm = get_permission(codename)
    user.user_permissions.add(perm)


def get_permission(codename):
    return Permission.objects.get(codename=codename)