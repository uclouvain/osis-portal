##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2018 Université catholique de Louvain (http://www.uclouvain.be)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
from unittest import mock

from django.http import HttpResponse
from django.test import TestCase, RequestFactory
from django.urls import reverse


class TestTrainingAutocomplete(TestCase):

    def setUp(self):
        self.url = reverse("training-autocomplete")
        self.request = RequestFactory()

    @mock.patch('requests.get')
    def test_when_filter(self, mock_get):
        mock_response = HttpResponse()
        mock_response.json = lambda *args, **kwargs: {"results": [{
            "uuid": "ABCD",
            "acronym": "TEST",
            "academic_year": "2019"
        }]}
        mock_get.return_value = mock_response
        response = self.client.get(self.url, data={'q': 'tes'})

        self.assertEqual(response.status_code, 200)

        expected_results = [{'id': 'ABCD', 'text': 'TEST - 2019'}]

        self.assertListEqual(response.json()['results'], expected_results)
