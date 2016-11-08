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
from admission.views import sociological
import admission.tests.data_for_tests as data_model
from admission.views.sociological import get_profession, get_other_profession

PROFESSION_EMPLOYEE = 'Employee'
CHECKED_STATUS = 'on'
UNCHECKED_STATUS = 'off'


class SociologicalTest(TestCase):

    def setUp(self):
        self.profession = data_model.create_profession(PROFESSION_EMPLOYEE, False)

    def test_get_boolean_status(self):
        self.assertTrue(sociological.get_boolean_status(CHECKED_STATUS))
        self.assertFalse(sociological.get_boolean_status(UNCHECKED_STATUS))
        self.assertFalse(sociological.get_boolean_status(''))

    def get_existing_profession(self):
        id = self.profession.id
        id_str = str(id)
        self.assertIs(get_profession(id, ''), self.profession)
        self.assertIs(get_profession(id_str, ''), self.profession)

    def get_non_existing_profession(self):
        self.assertIsNot(get_profession('11', ''), self.profession)

    def get_profession_by_name(self):
        self.assertIs(get_other_profession(PROFESSION_EMPLOYEE), self.profession)
        self.assertIsNot(get_other_profession(PROFESSION_EMPLOYEE+' de poste'), self.profession)

