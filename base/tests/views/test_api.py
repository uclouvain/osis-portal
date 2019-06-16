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

import json
from django.test import TestCase

from base.views import api


class TestApiTestCase(TestCase):

    def setUp(self):
        self.global_id = 12345678

    def test_get_user_roles(self):
        with open('osis_common/tests/ressources/person_roles_from_api.json') as json_file:
            expected_data = json.load(json_file)
            data = api.get_user_roles(self.global_id)
            self.assertDictEqual(expected_data, data)

    def test_get_managed_programs_as_dict(self):
        expected_results = {
            '2017': ['PHYS1BA', 'BIOL1BA'],
            '2018': ['PHYS1BA', 'BIOL1BA']
        }
        results = api.get_managed_programs_as_dict(self.global_id)
        self.assertDictEqual(expected_results, results)