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
from django.db.utils import IntegrityError
from django.test import TestCase

from base.tests.models import test_student
from internship.models import internship_choice as mdl_internship_choice
from internship.tests.factories.internship import InternshipFactory
from internship.tests.models import test_organization, test_internship_speciality


def create_internship_choice(organization, student, speciality, internship, choice=1):
    choice = mdl_internship_choice.InternshipChoice(organization=organization, student=student, speciality=speciality,
                                                    choice=choice, internship=internship, priority=False)
    choice.save()
    return choice


class TestSearch(TestCase):
    def setUp(self) -> None:
        self.organization = test_organization.create_organization()
        self.student = test_student.create_student("64641200")
        self.other_student = test_student.create_student("60601200")
        self.speciality = test_internship_speciality.create_speciality()
        self.other_speciality = test_internship_speciality.create_speciality()
        self.internship = InternshipFactory(speciality=self.speciality)
        self.other_internship = InternshipFactory(speciality=self.speciality)

        self.choice_1 = create_internship_choice(self.organization, self.student, self.other_speciality,
                                                 internship=self.other_internship)
        self.choice_2 = create_internship_choice(self.organization, self.student, self.speciality,
                                                 internship=self.internship)
        self.choice_3 = create_internship_choice(self.organization, self.other_student, self.other_speciality,
                                                 internship=self.other_internship)
        self.choice_4 = create_internship_choice(self.organization, self.other_student, self.speciality,
                                                 internship=self.internship)

    def test_duplicates_are_forbidden(self):
        with self.assertRaises(IntegrityError):
            create_internship_choice(self.organization, self.student, self.speciality, internship=self.internship)

    def test_with_only_student(self):
        choices = list(mdl_internship_choice.search(student=self.student))
        self.assertEqual(len(choices), 2)
        self.assertIn(self.choice_1, choices)
        self.assertIn(self.choice_2, choices)

    def test_with_only_internship_choice(self):
        choices = list(mdl_internship_choice.search(internship=self.other_internship))
        self.assertEqual(len(choices), 2)
        self.assertIn(self.choice_1, choices)
        self.assertIn(self.choice_3, choices)

    def test_with_only_speciality(self):
        choices = list(mdl_internship_choice.search(speciality=self.speciality))
        self.assertEqual(len(choices), 2)
        self.assertIn(self.choice_2, choices)
        self.assertIn(self.choice_4, choices)

    def test_with_student_and_internship_choice(self):
        choices = list(mdl_internship_choice.search(student=self.student, internship=self.internship))
        self.assertListEqual([self.choice_2], choices)

    def test_get_number_first_choice_by_organization(self):
        number_first_choice = list(mdl_internship_choice.get_number_first_choice_by_organization(
            self.speciality, self.internship
        ))
        expected = [{"organization": self.organization.id, "organization__count": 2}]
        self.assertEqual(expected, number_first_choice)

        other_organization = test_organization.create_organization(reference="10")
        yet_another_student = test_student.create_student("64641201")
        create_internship_choice(other_organization, yet_another_student, self.speciality, self.internship)
        number_first_choice = list(mdl_internship_choice.get_number_first_choice_by_organization(
            self.speciality, self.internship
        ))
        expected = [{"organization": self.organization.id, "organization__count": 2},
                    {"organization": other_organization.id, "organization__count": 1}]
        self.assertCountEqual(number_first_choice, expected)
        self.assertIn(expected[0], number_first_choice)
        self.assertIn(expected[1], number_first_choice)
