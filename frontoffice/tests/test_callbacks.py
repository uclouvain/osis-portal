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

from django.test import SimpleTestCase
from frontoffice.queue import callbacks
from reference.models.country import Country
from admission.models.offer_year import OfferYear


class TestCallbacks(SimpleTestCase):

    def test_get_list_model_fields_no_foreign_key(self):
        #  Test for model reference.country.Country
        list_expected = ["id", "iso_code", "name", "nationality", "european_union", "dialing_code", "cref_code"]
        list_actual = callbacks.get_model_fields(Country)
        self.assertListEqual(list_expected, list_actual)

    def test_get_list_model_fields_with_foreign_key(self):
        #  Test for model admission.offer_year.OfferYear
        list_expected = ["id", "external_id", "academic_year", "acronym", "title", "title_international",
                         "domain", "grade_type", "subject_to_quota"]
        list_actual = callbacks.get_model_fields(OfferYear)
        self.assertListEqual(list_expected, list_actual)


