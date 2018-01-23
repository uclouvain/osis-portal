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

from internship.models import organization as mdl_organization
from django.test import TestCase
from internship.tests.factories.cohort import CohortFactory


def create_organization(name="OSIS", acronym="OSIS", reference="01", cohort=None, city="test"):
    if cohort is None:
        cohort = CohortFactory()
    organization = mdl_organization.Organization(name=name, acronym=acronym, reference=reference, cohort=cohort,
                                                 city=city)
    organization.save()
    return organization


class TestSearch(TestCase):
    def setUp(self):
        self.cohort = CohortFactory()
        self.organization = create_organization(cohort=self.cohort)
        self.organization2 = create_organization(name="OSAS", reference="02", cohort=self.cohort)

    def test_with_specific_name(self):
        organizations = list(mdl_organization.search(self.cohort, name="OSIS"))
        self.assertListEqual(organizations, [self.organization])

    def test_with_no_match(self):
        organizations = list(mdl_organization.search(self.cohort, "NO MATCH"))
        self.assertFalse(organizations)

    def test_with_prefix(self):
        organizations = list(mdl_organization.search(self.cohort, "OS"))
        self.assertEqual(len(organizations), 2)
        self.assertIn(self.organization, organizations)
        self.assertIn(self.organization2, organizations)


class TestGetAllCities(TestCase):
    def test_with_no_data(self):
        cities = mdl_organization.get_all_cities()
        self.assertFalse(cities)

    def test_with_one_city(self):
        create_organization()
        cities = mdl_organization.get_all_cities()
        self.assertListEqual(['test'], cities)

    def test_with_two_same_cities(self):
        self.organization = create_organization()
        self.organization_2 = create_organization(reference='02')
        self.organization_3 = create_organization(reference='03')
        create_organization(city="city")
        cities = mdl_organization.get_all_cities()
        self.assertListEqual(["city", "test"], cities)


class TestGetHospitals(TestCase):
    def setUp(self):
        self.cohort = CohortFactory()
        self.organization_1 = create_organization(cohort=self.cohort, city="city1")
        self.organization_2 = create_organization(reference='02', cohort=self.cohort, city="city2")
        self.organization_3 = create_organization(name="OSAS", reference='03', cohort=self.cohort, city="city1")

    def test_with_no_criteria(self):
        hospitals = mdl_organization.search(self.cohort)
        self.assertEqual(len(hospitals), 3)
        self.assertIn(self.organization_1, hospitals)
        self.assertIn(self.organization_2, hospitals)
        self.assertIn(self.organization_3, hospitals)

    def test_with_name(self):
        hospitals = mdl_organization.search(self.cohort, name="OSIS")
        self.assertEqual(len(hospitals), 2)
        self.assertIn(self.organization_1, hospitals)
        self.assertIn(self.organization_2, hospitals)

    def test_with_city(self):
        hospitals = mdl_organization.search(self.cohort, city="city1")
        self.assertEqual(len(hospitals), 2)
        self.assertIn(self.organization_1, hospitals)
        self.assertIn(self.organization_3, hospitals)

    def test_with_name_and_city(self):
        hospitals = mdl_organization.search(self.cohort, name="OSIS", city="city2")
        self.assertEqual(len(hospitals), 1)
        self.assertIn(self.organization_2, hospitals)