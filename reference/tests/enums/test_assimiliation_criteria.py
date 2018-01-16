##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2017-2018 Université catholique de Louvain (http://www.uclouvain.be)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
from django.test import SimpleTestCase

from reference.enums import assimilation_criteria

class TestMethods(SimpleTestCase):
    def test_find_with_invalid_key(self):
        criteria_to_find = "UNKNOWN CRITERIA"
        self.assertIsNone(assimilation_criteria.find(criteria_to_find))

    def test_find_with_valid_key(self):
        criteria_to_find = assimilation_criteria.CRITERIA_3
        expected_answer = assimilation_criteria.ASSIMILATION_CRITERIA_CHOICES[2]
        self.assertEqual(assimilation_criteria.find(criteria_to_find), expected_answer)