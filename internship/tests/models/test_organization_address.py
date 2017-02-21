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
from internship.models import organization_address as mdl_organization_address
from internship.tests.models import test_organization


def create_organization_address(organization, city="test"):
    an_organization_address = mdl_organization_address.OrganizationAddress(organization=organization, label="label",
                                                                           location="location", city=city,
                                                                           postal_code="00", country="country")
    an_organization_address.save()
    return an_organization_address


class TestOrganizationAddress(TestCase):
    def setUp(self):
        self.organization = test_organization.create_organization()
        self.organization_2 = test_organization.create_organization(reference='02')

    def test_get_all_cities_with_no_data(self):
        cities = mdl_organization_address.get_all_cities()
        self.assertFalse(cities)

    def test_get_all_cities(self):
        create_organization_address(self.organization)
        cities = mdl_organization_address.get_all_cities()
        self.assertListEqual(['test'], cities)

    def test_get_all_cities_with_two_same_cities(self):
        create_organization_address(self.organization)
        create_organization_address(self.organization_2)
        create_organization_address(self.organization, city="city")
        cities = mdl_organization_address.get_all_cities()
        self.assertListEqual(["city", "test"], cities)
