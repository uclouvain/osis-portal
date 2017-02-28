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
from internship.models import internship_choice as mdl_internship_choice
from internship.tests.models import test_organization, test_internship_speciality
from base.tests.models import test_student


def create_internship_choice(organization, student, speciality, internship_choice=0):
    choice = mdl_internship_choice.InternshipChoice(organization=organization, student=student, speciality=speciality,
                                                    choice=1, internship_choice=internship_choice, priority=False)
    choice.save()
    return choice


class TestSearch(TestCase):
    def setUp(self):
        self.organization = test_organization.create_organization()
        self.student = test_student.create_student("64641200")
        self.other_student = test_student.create_student("60601200")
        self.speciality = test_internship_speciality.create_speciality()

        self.choice_1 = create_internship_choice(self.organization, self.student, self.speciality)
        self.choice_2 = create_internship_choice(self.organization, self.student, self.speciality, internship_choice=1)
        self.choice_3 = create_internship_choice(self.organization, self.other_student, self.speciality)

    def test_with_only_student(self):
        choices = list(mdl_internship_choice.search(student=self.student))
        self.assertEqual(len(choices), 2)
        self.assertIn(self.choice_1, choices)
        self.assertIn(self.choice_2, choices)

    def test_with_only_internship_choice(self):
        choices = list(mdl_internship_choice.search(internship_choice=0))
        self.assertEqual(len(choices), 2)
        self.assertIn(self.choice_1, choices)
        self.assertIn(self.choice_3, choices)

    def test_with_student_and_internship_choice(self):
        choices = list(mdl_internship_choice.search(student=self.student, internship_choice=1))
        self.assertListEqual([self.choice_2], choices)








