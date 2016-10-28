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

from django.test import TestCase, RequestFactory

from django.conf import settings
from django.contrib.auth.models import User
from admission.models import applicant
from admission.views import application
from django.utils.encoding import force_text
import json
from admission import models as mdl
from django.contrib.auth.models import User
import admission.tests.data_for_tests as data_model
from django.test import Client
from reference.enums import institutional_grade_type
from django.test import RequestFactory


class ApplicationTest(TestCase):

    def setUp(self):
        a_user = User.objects.create_user(
            username='jacob', email='jacob@gmail.com', password='top_secret')
        self.applicant = data_model.create_applicant_by_user(a_user)
        self.application = data_model.create_application(self.applicant)

    def test_create_application_assimilation_criteria_from_applicant_assimilation_criteria(self):
        data_model.create_applicant_assimilation_criteria(self.applicant)
        try:
            application.create_application_assimilation_criteria(self.application)
        except Exception:
            self.fail("{0} raised ExceptionType unexpectedly!"
                      .format("test_create_application_assimilation_criteria_from_applicant_assimilation_criteria"))

    def test_delete_existing_answers(self):
        try:
            application.delete_existing_answers(self.application)
        except Exception:
            self.fail("{0} raised ExceptionType unexpectedly!"
                      .format("test_create_application_assimilation_criteria_from_applicant_assimilation_criteria"))

    def test_create_answers_txt_question(self):
        request_factory = RequestFactory()
        my_request = request_factory.get("", {'txt_answer_question_1': 'Answer txt question 1'})
        try:
            application.create_answers(self.application, my_request)
        except Exception:
            self.fail("{0} raised ExceptionType unexpectedly!".format("test_create_answers_txt_question"))

    def test_create_answers_txt_radio(self):
        request_factory = RequestFactory()
        my_request = request_factory.get("", {'txt_answer_radio_1': 'Answer txt radio 1'})
        try:
            application.create_answers(self.application, my_request)
        except Exception:
            self.fail("{0} raised ExceptionType unexpectedly!".format("test_create_answers_txt_radio"))

    def test_create_answers_txt_checkbox(self):
        request_factory = RequestFactory()
        my_request = request_factory.get("", {'txt_answer_checkbox_1': 'Answer txt checkbox 1'})
        try:
            application.create_answers(self.application, my_request)
        except Exception:
            self.fail("{0} raised ExceptionType unexpectedly!".format("test_create_answers_txt_checkbox"))

    def test_create_answers_txt_select(self):
        request_factory = RequestFactory()
        my_request = request_factory.get("", {'slt_question_1': 'Answer slt_question_ 1'})
        try:
            application.create_answers(self.application, my_request)
        except Exception:
            self.fail("{0} raised ExceptionType unexpectedly!".format("test_create_answers_txt_select"))

    def test_delete_application_assimilation_criteria(self):
        try:
            application.delete_application_assimilation_criteria(self.application)
        except Exception:
            self.fail("{0} raised ExceptionType unexpectedly!".format("test_create_answers_txt_select"))
