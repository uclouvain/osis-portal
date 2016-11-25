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
from admission.utils import send_mail
from admission.models import applicant
from django.core.management import call_command
from django.contrib.auth.models import User

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
            username='jacob', email='person@localhost', password='top_secret')
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
