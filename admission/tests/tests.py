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
from django.core.management import call_command
from django.contrib.auth.models import User

from admission.utils import send_mail
from admission.models import applicant


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
