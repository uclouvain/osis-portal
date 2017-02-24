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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
from django.http import HttpRequest
from django.test import TestCase

from reference.tests.models import test_education_institution
from admission.views import places
from reference import models as mdl_reference
from reference.enums import education_institution_type

CITY_KEY = 'city'
POSTAL_CODE_KEY = 'postal_code'

EXISTING_POSTAL_CODE = '5020'
NON_EXISTING_POSTAL_CODE = '5020Z'

EXISTING_CITY_NAME = 'Malonne'
NON_EXISTING_CITY_NAME = 'Malonne 99'


class PlacesTest(TestCase):

    def test_get_dict_postal_codes_from_existing_postal_code(self):
        data = places.get_dict_postal_codes(create_education_institutions_from_postal_code(EXISTING_POSTAL_CODE))
        self.assertEqual(data[0][POSTAL_CODE_KEY], EXISTING_POSTAL_CODE)

    def test_get_dict_postal_codes_from_non_existing_postal_code(self):
        data = places.get_dict_postal_codes(create_education_institutions_from_postal_code(NON_EXISTING_POSTAL_CODE))
        self.assertNotEqual(data[0][POSTAL_CODE_KEY], EXISTING_POSTAL_CODE)

    def test_get_dict_cities_names_from_existing_city(self):
        data = places.get_dict_cities_names(create_education_institutions_from_city(EXISTING_CITY_NAME))
        self.assertEqual(data[0][CITY_KEY], EXISTING_CITY_NAME)

    def test_get_dict_cities_names_from_non_existing_city(self):
        data = places.get_dict_cities_names(create_education_institutions_from_city(NON_EXISTING_CITY_NAME))
        self.assertNotEqual(data[0][CITY_KEY], EXISTING_CITY_NAME)


def create_education_institutions_from_postal_code(postal_code):
    return [test_education_institution.create_education_institution_from_postal_code(postal_code)]


def create_education_institutions_from_city(city):
    return [test_education_institution.create_education_institution_from_city(city)]
