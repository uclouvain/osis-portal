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
from django.conf import settings
from django.contrib.auth.models import User
from admission.models import applicant
from admission.views import secondary_education
from django.utils.encoding import force_text
import json
from admission import models as mdl
from django.contrib.auth.models import User
import admission.tests.data_for_tests as data_model
from django.test import Client


class SecondaryEducationTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='jacob', email='jacob@gmail.com', password='top_secret')
        self.applicant = data_model.create_applicant_by_user(self.user)

    def test_get_secondary_education_exams_data_size(self):
        secondary_education_record = None
        list_secondary_education_exams = secondary_education.\
            get_secondary_education_exams(secondary_education_record)
        self.assertTrue(len(list_secondary_education_exams) == 0)

        secondary_education_record = data_model.create_secondary_education_with_exams()
        list_secondary_education_exams = secondary_education.\
            get_secondary_education_exams(secondary_education_record)
        self.assertTrue(len(list_secondary_education_exams) == 3)



    def test_secondary_education_exam_update(self):
        secondary_education_record = data_model.create_secondary_education_with_exams()
        type = 'ADMISSION'
        secondary_education_exam = data_model.create_secondary_education_exam(secondary_education_record, type)

        try:
            secondary_education.secondary_education_exam_update(secondary_education_record,
                                                                type,
                                                                secondary_education_exam)
        except ExceptionType:
            self.fail("secondary_education_exam_update raised ExceptionType unexpectedly!")

        try:
            secondary_education.secondary_education_exam_update(None, type, secondary_education_exam)
        except ExceptionType:
            self.fail("secondary_education_exam_update raised ExceptionType unexpectedly!")

        try:
            secondary_education.secondary_education_exam_update(None, None, secondary_education_exam)
        except ExceptionType:
            self.fail("secondary_education_exam_update raised ExceptionType unexpectedly!")

        try:
            secondary_education.secondary_education_exam_update(None, None, None)
        except Exception:
            self.fail("secondary_education_exam_update raised ExceptionType unexpectedly!")

    def test_get_secondary_education_files_data_existence(self):
        try:
            secondary_education.get_secondary_education_files(None)
        except Exception:
            self.fail("get_secondary_education_files_data raised ExceptionType unexpectedly!")
        an_application = data_model.create_application(self.applicant)
        try:
            secondary_education.get_secondary_education_files(an_application)
        except Exception:
            self.fail("get_secondary_education_files_data raised ExceptionType unexpectedly!")

        an_application_document_file = data_model.create_application_document_file(an_application,
                                                                                   self.user,
                                                                                   'NATIONAL_DIPLOMA_VERSO')

        dict = secondary_education.get_secondary_education_files(an_application)
        self.assertTrue(dict['national_diploma_verso'] == an_application_document_file)

