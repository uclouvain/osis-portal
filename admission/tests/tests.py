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
from admission.utils import pdf_utils
from reportlab.platypus import SimpleDocTemplate, Image
import os
from django.conf import settings
import io as io
from django.contrib.auth.models import User
from admission.utils import send_mail
from admission.models import applicant
from django.core.management import call_command
from admission.views import assimilation_criteria, secondary_education
from django.utils.encoding import force_text
import json
from admission import models as mdl
from django.contrib.auth.models import User
import admission.tests.data_for_tests as data_model
from django.test import Client

ASSETS_PATH = os.path.join(settings.BASE_DIR, 'admission/tests/assets/')
PDF1 = "pdf1.pdf"
PDF2 = "pdf2.pdf"


class PdfTest(TestCase):

    def test_allowed_file(self):
        self.assertEqual(pdf_utils.allowed_file('test.pdf'), False)
        self.assertEqual(pdf_utils.allowed_file('test.GIF'), True)
        self.assertEqual(pdf_utils.allowed_file('test.Gif'), True)
        self.assertEqual(pdf_utils.allowed_file('testGIF'), False)
        self.assertEqual(pdf_utils.allowed_file('test.jpg'), True)

    def test_convert_image_to_pdf(self):
        image_file = ASSETS_PATH + "gif_2625_2154.gif"
        filename = "test.pdf"
        self.assertIsInstance(pdf_utils.convert_image_to_pdf(image_file, filename), SimpleDocTemplate)
        filename = "test"
        self.assertIsNone(pdf_utils.convert_image_to_pdf(image_file, filename))
        image_file = ASSETS_PATH + "text.txt"
        filename = "test.pdf"
        self.assertIsNone(pdf_utils.convert_image_to_pdf(image_file, filename))
        image_file = ASSETS_PATH + "gif_2625_2154.GIF"
        filename = "test.pdf"
        self.assertIsNone(pdf_utils.convert_image_to_pdf(image_file, filename))

    def test_create_cover_sheet(self):
        document_list = None
        noma = None
        self.assertIsNone(pdf_utils.create_cover_sheet(document_list, noma))
        document_list = []
        noma = None
        self.assertIsNone(pdf_utils.create_cover_sheet(document_list, noma))
        document_list = ['id card', 'score sheet']
        noma = None
        self.assertIsNotNone(pdf_utils.create_cover_sheet(document_list, noma))
        document_list = ['id card', 'score sheet']
        noma = "12345678"
        self.assertIsNotNone(pdf_utils.create_cover_sheet(document_list, noma))

    def test_create_pdf_with_cover(self):
        pdf_list = None
        document_list = None
        noma = None
        self.assertIsNone(pdf_utils.create_pdf_with_cover(document_list, pdf_list, noma))
        pdf_list = []
        document_list = ['document1', 'document2', 'document3']
        noma = '123456789'
        self.assertIsNotNone(pdf_utils.create_pdf_with_cover(document_list, pdf_list, noma))
        pdf_list = [ASSETS_PATH + PDF1, ASSETS_PATH + PDF2]
        self.assertIsInstance(pdf_utils.create_pdf_with_cover(document_list, pdf_list, noma), io.IOBase)
        pdf_list = [ASSETS_PATH + "pdf1.pdff", ASSETS_PATH + PDF2]
        self.assertIsInstance(pdf_utils.create_pdf_with_cover(document_list, pdf_list, noma), io.IOBase)

    def test_merge_pdfs(self):
        pdf_list = None
        self.assertIsNone(pdf_utils.merge_pdfs(pdf_list))
        pdf_list = []
        self.assertIsNone(pdf_utils.merge_pdfs(pdf_list))
        pdf_list = [ASSETS_PATH + PDF1, ASSETS_PATH + PDF2]
        self.assertIsInstance(pdf_utils.merge_pdfs(pdf_list), io.IOBase)
        pdf_list = [ASSETS_PATH + 'pdf1.pdff', ASSETS_PATH + 'pdf2.pdff']
        self.assertIsNone(pdf_utils.merge_pdfs(pdf_list))
        pdf_list = [ASSETS_PATH + 'pdf1.pdff', ASSETS_PATH + PDF2]
        self.assertIsInstance(pdf_utils.merge_pdfs(pdf_list), io.IOBase)

    def test_resize_image(self):
        image_file = ASSETS_PATH + "gif_2625_2154.gif"
        self.assertIsInstance(pdf_utils.resize_image(image_file), Image)
        image_file = ASSETS_PATH + "text.txt"
        self.assertIsNone(pdf_utils.resize_image(image_file))
        image_file = ASSETS_PATH + "gif_2625_2154.GIF"
        self.assertIsNone(pdf_utils.resize_image(image_file))


class SendMailTest(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='jacob', email='jacob@gmail.com', password='top_secret')
        applicant.Applicant.objects.create(user=self.user, gender="MALE")
        call_command("loaddata", "message_templates.json", verbosity=0)

    def test_send_mail_activation(self):

        request = self.factory.get('application/accounting/')
        request.user = self.user
        activation_code = "uuu"
        an_applicant = applicant.Applicant.objects.get(user=request.user)

        self.assertIsNotNone(send_mail.send_mail_activation(request,
                                                            activation_code,
                                                            an_applicant,
                                                            'account_activation_bidon'))
        self.assertIsNone(send_mail.send_mail_activation(request,
                                                         activation_code,
                                                         an_applicant,
                                                         'account_activation'))


class AssimilationCriteriaTest(TestCase):

    def test_criteria1(self):
        list_document_type = []
        list_document_type = assimilation_criteria.criteria1(list_document_type)
        self.assertTrue(len(list_document_type) == 2)

        list_document_type = assimilation_criteria.criteria1(None)
        self.assertTrue(len(list_document_type) == 2)

        list_document_type = []
        assimilation_doc = assimilation_criteria.AssimilationDoc()
        assimilation_doc.criteria_id = 1
        list_document_type.append(assimilation_doc)
        list_document_type = assimilation_criteria.criteria1(list_document_type)
        self.assertTrue(len(list_document_type) == 3)

    def test_criteria2(self):
        list_document_type = []
        list_document_type = assimilation_criteria.criteria2(list_document_type)
        self.assertTrue(len(list_document_type) == 5)

        list_document_type = assimilation_criteria.criteria2(None)
        self.assertTrue(len(list_document_type) == 5)

        list_document_type = []
        assimilation_doc = assimilation_criteria.AssimilationDoc()
        assimilation_doc.criteria_id = 2
        list_document_type.append(assimilation_doc)
        list_document_type = assimilation_criteria.criteria2(list_document_type)
        self.assertTrue(len(list_document_type) == 6)

    def test_find_list_document_type_by_criteria(self):
        list_document_type = assimilation_criteria.find_list_document_type_by_criteria(None)
        self.assertTrue(len(list_document_type) == 0)

        list_document_type = assimilation_criteria.find_list_document_type_by_criteria("1")
        self.assertTrue(len(list_document_type) == 0)

        list_document_type = assimilation_criteria.find_list_document_type_by_criteria(1)
        self.assertTrue(len(list_document_type) == 2)

    def test_get_list_docs(self):
        list_document_type = assimilation_criteria.get_list_docs(None)
        self.assertTrue(len(list_document_type) == 0)

        list_document_type = assimilation_criteria.get_list_docs("1")
        self.assertTrue(len(list_document_type) == 0)

        list_document_type = assimilation_criteria.get_list_docs(3)
        self.assertTrue(len(list_document_type) == 9)


class SecondaryEducationTest(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='jacob', email='jacob@gmail.com', password='top_secret')
        self.applicant = data_model.create_applicant_by_user(self.user)

    def test_get_secondary_education_exams_data(self):
        secondary_education_record = None
        list_secondary_education_exams = secondary_education.\
            get_secondary_education_exams_data(secondary_education_record)
        self.assertTrue(len(list_secondary_education_exams) == 0)

        secondary_education_record = data_model.create_secondary_education_with_exams()
        list_secondary_education_exams = secondary_education.\
            get_secondary_education_exams_data(secondary_education_record)
        self.assertTrue(len(list_secondary_education_exams) == 3)

    def test_is_local_language_exam_needed(self):
        self.assertFalse(secondary_education.is_local_language_exam_needed(None))

        # a_user = data_model.create_user()
        self.assertFalse(secondary_education.is_local_language_exam_needed(self.user))

        an_application = data_model.create_application(self.applicant)
        self.assertFalse(secondary_education.is_local_language_exam_needed(self.user))

        an_application.offer_year.grade_type = data_model.create_grade_type('BACHELOR')
        an_application.offer_year.save()
        self.assertTrue(secondary_education.is_local_language_exam_needed(self.user))

        an_application.offer_year.grade_type = data_model.create_grade_type('BACHELORZ')
        an_application.offer_year.save()
        self.assertFalse(secondary_education.is_local_language_exam_needed(self.user))

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

    def test_get_secondary_education_files_data(self):
        try:
            secondary_education.get_secondary_education_files_data(None)
        except:
            self.fail("get_secondary_education_files_data raised ExceptionType unexpectedly!")
        an_application = data_model.create_application(self.applicant)
        try:
            secondary_education.get_secondary_education_files_data(an_application)
        except Exception:
            self.fail("get_secondary_education_files_data raised ExceptionType unexpectedly!")

        an_application_document_file = data_model.create_application_document_file(an_application,
                                                                                   self.user,
                                                                                   'NATIONAL_DIPLOMA_VERSO')

        dict = secondary_education.get_secondary_education_files_data(an_application)
        self.assertTrue(dict['national_diploma_verso'] == an_application_document_file)
