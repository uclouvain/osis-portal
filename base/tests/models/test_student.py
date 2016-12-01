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
from base.tests.models.test_person import create_person
from base import models as mdl_base
from base.models import student as mdl_student


class TestModelStudent(TestCase):
    def setUp(self):
        self.student = create_student()

    def test_get_student_by_registration_id(self):
        student = mdl_student.get_student_by_registration_id("64641200")
        self.assertEqual(student, self.student, "Wrong student returned")

        student = mdl_student.get_student_by_registration_id("6587984")
        self.assertIsNone(student, "Should return none")


def create_student(registration_id="64641200"):
    a_student = mdl_base.student.Student(registration_id=registration_id, person=create_person())
    a_student.save()
    return a_student


def create_student_with_specific_registration_id(registration_id):
    a_student = mdl_base.student.Student(registration_id=registration_id, person=create_person())
    a_student.save()
    return a_student