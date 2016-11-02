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

import json
from django.contrib.auth.models import User
from django.test import TestCase, RequestFactory

import admission.tests.data_for_tests as data_model
from admission.models import applicant
from admission.models.enums import document_type
from admission.views import upload_file

DESCRIPTION = document_type.INTERNATIONAL_DIPLOMA_RECTO


class UploadFileTest(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='jacob', email='jacob@gmail.com', password='top_secret')
        self.applicant = data_model.create_applicant_by_user(self.user)
        self.application = data_model.create_application(self.applicant)
        self.application_document_file = data_model.create_application_document_file(self.application,
                                                                                     self.applicant.user.username,
                                                                                     DESCRIPTION)

    def test_delete_existing_application_documents(self):
        try:
            upload_file.delete_existing_application_documents(self.application, DESCRIPTION)
        except Exception:
            self.fail("delete_existing_application_documents raised ExceptionType unexpectedly!")

    def test_delete_existing_applicant_documents(self):
        data_model.create_applicant_document_file(self.applicant, DESCRIPTION)
        try:
            upload_file.delete_existing_applicant_documents(self.applicant, DESCRIPTION)
        except Exception:
            self.fail("delete_existing_application_documents raised ExceptionType unexpectedly!")

    def test_find_document_by_application_and_description(self):
        my_request = self.factory.get('/document_application',
                                      {'description': self.application_document_file.document_file.description,
                                       'application': self.application_document_file.application.id})
        self.assertIsNotNone(
            upload_file.find_by_description_application(my_request))

