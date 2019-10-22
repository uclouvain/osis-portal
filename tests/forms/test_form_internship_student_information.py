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

from internship.forms import form_internship_student_information


class TestSearchHospitalForm(TestCase):
    def setUp(self):
        self.data = {
            "location": "location",
            "postal_code": "postal",
            "city": "city",
            "country": "country",
            "email": "test@test.com",
            "phone_mobile": "0236478987",
            "contest": "GENERALIST"
        }

    def test_null_location(self):
        self.data["location"] = ""
        form = form_internship_student_information.InternshipStudentInformationForm(data=self.data)
        self.assertFalse(form.is_valid())

    def test_null_postal_code(self):
        self.data["postal_code"] = ""
        form = form_internship_student_information.InternshipStudentInformationForm(data=self.data)
        self.assertFalse(form.is_valid())

    def test_null_city(self):
        self.data["city"] = ""
        form = form_internship_student_information.InternshipStudentInformationForm(data=self.data)
        self.assertFalse(form.is_valid())

    def test_null_country(self):
        self.data["country"] = ""
        form = form_internship_student_information.InternshipStudentInformationForm(data=self.data)
        self.assertFalse(form.is_valid())

    def test_correct_form(self):
        form = form_internship_student_information.InternshipStudentInformationForm(data=self.data)
        self.assertTrue(form.is_valid())
