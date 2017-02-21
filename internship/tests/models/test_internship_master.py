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
from django.test import TestCase
from internship.models import internship_master as mdl_internship_master
from internship.tests.models import test_organization


def create_internship_master(organization, name="Master", speciality="radiologie"):
    master = mdl_internship_master.InternshipMaster(organization=organization, last_name=name,
                                                    speciality=speciality)
    master.save()
    return master


class TestSearch(TestCase):
    def setUp(self):
        self.organization = test_organization.create_organization()
        self.organization_2 = test_organization.create_organization(reference="02")
        self.master_1 = create_internship_master(self.organization, name="master_1")
        self.master_2 = create_internship_master(self.organization, name="master_2", speciality="medecine")
        self.master_3 = create_internship_master(self.organization_2, name="master_3")

    def test_with_specific_name(self):
        masters = list(mdl_internship_master.search(name="master_1"))
        self.assertListEqual(masters, [self.master_1])

    def test_with_prefix_name(self):
        masters = list(mdl_internship_master.search(name="master"))
        self.assertEqual(len(masters), 3)
        self.assertIn(self.master_1, masters)
        self.assertIn(self.master_2, masters)
        self.assertIn(self.master_3, masters)

    def test_with_no_criteria(self):
        masters = mdl_internship_master.search()
        self.assertFalse(masters)

    def test_with_speciality(self):
        masters = list(mdl_internship_master.search(speciality="radiologie"))
        self.assertEqual(len(masters), 2)
        self.assertIn(self.master_1, masters)
        self.assertIn(self.master_3, masters)

    def test_with_organization(self):
        masters = list(mdl_internship_master.search(organization=self.organization))
        self.assertEqual(len(masters), 2)
        self.assertIn(self.master_1, masters)
        self.assertIn(self.master_2, masters)

    def test_with_two_criteria(self):
        masters = list(mdl_internship_master.search(name="master", speciality="radiologie"))
        self.assertEqual(len(masters), 2)
        self.assertIn(self.master_1, masters)
        self.assertIn(self.master_3, masters)

        masters = list(mdl_internship_master.search(name="master", organization=self.organization_2))
        self.assertEqual(len(masters), 1)
        self.assertIn(self.master_3, masters)

        masters = list(mdl_internship_master.search(speciality="radiologie", organization=self.organization))
        self.assertEqual(len(masters), 1)
        self.assertIn(self.master_1, masters)

    def test_with_all_criteria(self):
        masters = list(mdl_internship_master.search(name="master_1", speciality="radiologie",
                                                    organization=self.organization))
        self.assertEqual(len(masters), 1)
        self.assertIn(self.master_1, masters)


class TestGetAllSpecialities(TestCase):
    def setUp(self):
        self.organization = test_organization.create_organization()

    def test_with_no_master(self):
        specialities = mdl_internship_master.get_all_specialities()
        self.assertFalse(specialities)

    def test_with_one_master(self):
        create_internship_master(self.organization)

        specialities = mdl_internship_master.get_all_specialities()
        self.assertListEqual(specialities, ['radiologie'])

    def test_with_two_masters_with_same_speciality(self):
        create_internship_master(self.organization, name="master1")
        create_internship_master(self.organization, name="master2")

        specialities = mdl_internship_master.get_all_specialities()
        self.assertListEqual(specialities, ['radiologie'])

    def test_with_two_masters_with_different_speciality(self):
        create_internship_master(self.organization, name="master1")
        create_internship_master(self.organization, name="master2", speciality="medecine")

        specialities = mdl_internship_master.get_all_specialities()
        self.assertListEqual(specialities, ['medecine', 'radiologie'])






