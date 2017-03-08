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
from internship.models import internship_speciality as mdl_internship_speciality
from base.tests.models import test_learning_unit
from django.test import TestCase


def create_speciality(name="chirurgie", acronym="WSD"):
    learning_unit = test_learning_unit.create_learning_unit({"title": "stage medecine",
                                                             "acronym": "WSD"})
    speciality = mdl_internship_speciality.InternshipSpeciality(learning_unit=learning_unit, name=name, acronym=acronym)
    speciality.save()
    return speciality


class TestInternshipSpeciality(TestCase):
    def setUp(self):
        self.speciality_1 = create_speciality(name="spec1")
        self.speciality_2 = create_speciality(name="spec2")
        self.speciality_2.mandatory = True
        self.speciality_2.save()

    def test_find_non_mandatory(self):
        actual = list(mdl_internship_speciality.find_non_mandatory())
        self.assertEqual(len(actual), 1)
        self.assertIn(self.speciality_1, actual)






