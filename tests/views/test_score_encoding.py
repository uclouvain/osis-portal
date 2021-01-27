##############################################################################
#
# OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2021 Université catholique de Louvain (http://www.uclouvain.be)
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
import uuid

import mock
from django.test import TestCase, override_settings
from django.urls import reverse

from base.tests.factories.user import UserFactory
from internship.tests.views.test_api_client import MockAPI


@override_settings(URL_INTERNSHIP_API='url_test_api')
class TestScoreEncoding(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.client.force_login(self.user)
        self.api_patcher = mock.patch("internship.views.api_client.InternshipAPIClient.__new__", return_value=MockAPI)
        self.api_patcher.start()
        self.addCleanup(self.api_patcher.stop)

    def test_access_score_encoding(self):
        url = reverse('internship_score_encoding')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'internship_score_encoding.html')

    def test_redirect_to_login_page(self):
        self.client.logout()
        url = reverse('internship_score_encoding')
        response = self.client.get(url)
        self.assertRedirects(response, reverse('internship_score_encoding_login')+"?next={}".format(url))

    def test_access_score_encoding_sheet(self):
        url = reverse('internship_score_encoding_sheet', kwargs={
            'specialty_uuid': str(uuid.uuid4()),
            'organization_uuid': str(uuid.uuid4())
        })
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'internship_score_encoding_sheet.html')

    def test_access_score_encoding_sheet_detail(self):
        url = reverse('internship_score_encoding_form', kwargs={
            'specialty_uuid': str(uuid.uuid4()),
            'organization_uuid': str(uuid.uuid4()),
            'affectation_uuid': str(uuid.uuid4())
        })
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'internship_score_encoding_form.html')

    def test_post_score_encoding_form(self):
        url = reverse('internship_score_encoding_form', kwargs={
            'specialty_uuid': str(uuid.uuid4()),
            'organization_uuid': str(uuid.uuid4()),
            'affectation_uuid': str(uuid.uuid4())
        })
        response = self.client.post(url, data={'apd_1': 'A'})
        self.assertEqual(response.status_code, 302)
