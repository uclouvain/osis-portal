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
from django.contrib import messages
from django.contrib.messages import SUCCESS
from django.test import TestCase, override_settings
from django.urls import reverse

from base.tests.factories.user import UserFactory
from internship.models.score_encoding_utils import APDS, MIN_APDS, MAX_APDS
from internship.tests.services.test_api_client import MockAPI


@override_settings(URL_INTERNSHIP_API='url_test_api')
class TestScoreEncoding(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory()
        cls.api_patcher = mock.patch("internship.services.api_client.InternshipAPIClient.__new__", return_value=MockAPI)

    def setUp(self):
        self.client.force_login(self.user)
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
        self.assertRedirects(response, reverse('login')+"?next={}".format(url))

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

    def test_post_score_encoding_form_not_valid_too_many_apds(self):
        apds_data = {apd: 'A' for apd in APDS}
        url = reverse('internship_score_encoding_form', kwargs={
            'specialty_uuid': str(uuid.uuid4()),
            'organization_uuid': str(uuid.uuid4()),
            'affectation_uuid': str(uuid.uuid4())
        })
        response = self.client.post(url, data=apds_data)
        messages_list = [item.message for item in messages.get_messages(response.wsgi_request)]
        self.assertEqual(response.status_code, 200)
        self.assertIn(str(MIN_APDS), messages_list[0])
        self.assertIn(str(MAX_APDS), messages_list[0])

    def test_post_score_encoding_form_not_valid_too_few_apds(self):
        url = reverse('internship_score_encoding_form', kwargs={
            'specialty_uuid': str(uuid.uuid4()),
            'organization_uuid': str(uuid.uuid4()),
            'affectation_uuid': str(uuid.uuid4())
        })
        response = self.client.post(url, data={'apd_1': 'A'})
        messages_list = [item.message for item in messages.get_messages(response.wsgi_request)]
        self.assertEqual(response.status_code, 200)
        self.assertIn(str(MIN_APDS), messages_list[0])
        self.assertIn(str(MAX_APDS), messages_list[0])

    def test_post_score_encoding_form_valid(self):
        apds_data = {'apd_{}'.format(apd): 'A' for apd in range(1, MAX_APDS - 1)}
        url = reverse('internship_score_encoding_form', kwargs={
            'specialty_uuid': str(uuid.uuid4()),
            'organization_uuid': str(uuid.uuid4()),
            'affectation_uuid': str(uuid.uuid4())
        })
        response = self.client.post(url, data=apds_data)
        messages_items = [item for item in messages.get_messages(response.wsgi_request)]
        self.assertEqual(response.status_code, 302)
        self.assertEqual(messages_items[0].level, SUCCESS)

    @mock.patch('internship.tests.services.test_api_client.MockAPI.scores_affectation_uuid_validate_post')
    def test_score_validation_success(self, mock_validation_response):
        mock_validation_response.return_value = {}, 204, {}
        url = reverse('internship_score_encoding_validate', kwargs={'affectation_uuid': str(uuid.uuid4())})
        json_response = self.client.get(url).json()
        self.assertDictEqual(json_response, {})

    @mock.patch('internship.tests.services.test_api_client.MockAPI.scores_affectation_uuid_validate_post')
    def test_score_validation_fail(self, mock_validation_response):
        mock_validation_response.return_value = {'error': 'error'}, 404, {}
        url = reverse('internship_score_encoding_validate', kwargs={'affectation_uuid': str(uuid.uuid4())})
        json_response = self.client.get(url).json()
        self.assertDictEqual(json_response, {'error': 'An error occured during validation'})

