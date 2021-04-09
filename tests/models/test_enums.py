##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2021 Université catholique de Louvain (http://www.uclouvain.be)
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
from django.test.testcases import TestCase

from internship.models.enums.civility import Civility


class TestEnums(TestCase):
    def test_civility(self):
        for civility in [civility for civility in dir(Civility) if not civility.startswith('__')]:
            value = Civility.__getattr__(civility)._value_
            self.assertIn(value, str(Civility.choices()))

    def test_civility_acronym(self):
        dr_acronym = Civility.get_acronym(Civility.DOCTOR.name)
        prof_acronym = Civility.get_acronym(Civility.PROFESSOR.name)
        self.assertEqual(dr_acronym, "Dr.")
        self.assertEqual(prof_acronym, "Prof.")
