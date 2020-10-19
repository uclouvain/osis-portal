#############################################################################
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
from django.contrib.auth.models import Group
from django.test import TestCase

from base.models.student import Student
from base.tests.factories.person import PersonFactory
from base.tests.factories.student import StudentFactory
from base.business import student as student_bsn


class TestPersonIsStudent(TestCase):
    def setUp(self):
        Group.objects.create(name='students')
        self.person = PersonFactory()
        self.student = StudentFactory(person=self.person)

    def test_check_is_student_with_one_student(self):
        self.assertTrue(student_bsn.check_if_person_is_student(self.person))

    def test_check_is_student_with_more_than_one_student(self):
        student2 = StudentFactory(person=self.person)
        student3 = StudentFactory(person=self.person)

        students_for_person = Student.objects.filter(person=self.person)
        self.assertTrue(len(students_for_person) > 1)
        self.assertTrue(student_bsn.check_if_person_is_student(self.person))

    def test_check_is_not_student(self):
        person_not_student = PersonFactory()
        self.assertFalse(student_bsn.check_if_person_is_student(person_not_student))
