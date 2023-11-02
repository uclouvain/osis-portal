##############################################################################
#
# OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2023 Université catholique de Louvain (http://www.uclouvain.be)
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
from unittest import skip

import mock
from django.contrib.auth.models import Permission
from django.test import TestCase, override_settings
from django.urls import reverse

from base.tests.factories.person import PersonFactory
from base.tests.factories.student import StudentFactory
from internship.tests.services.test_api_client import MockAPI


@override_settings(URL_INTERNSHIP_API='url_test_api')
class TestPlaceEvaluation(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.person = PersonFactory()
        cls.student = StudentFactory(registration_id="45451298", person=cls.person)
        perm = Permission.objects.get(codename="can_access_internship", content_type__model='internshipoffer')
        cls.person.user.user_permissions.add(perm)

    def setUp(self):
        self.api_patcher = mock.patch(
            "internship.services.internship.InternshipAPIClient.__new__",
            return_value=MockAPI
        )
        self.client.force_login(self.person.user)
        self.api_patcher.start()
        self.addCleanup(self.api_patcher.stop)

    @skip
    def test_view_place_evaluations_list(self):
        url = reverse('place_evaluation_list', kwargs={'cohort_id': "cohort"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'place_evaluation_list.html')

    @skip
    def test_view_place_evaluation_form(self):
        url = reverse('place_evaluation', kwargs={'cohort_id': "cohort", 'period_name': 'P1'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'place_evaluation_form.html')

    @skip
    @mock.patch('internship.services.internship.InternshipAPIService.update_evaluation')
    def test_post_place_evaluation_form(self, mock_update_evaluation):
        url = reverse('place_evaluation', kwargs={'cohort_id': "cohort", 'period_name': 'P1'})
        response = self.client.post(url, data={'evaluation': {'key': 'value'}})
        self.assertTrue(mock_update_evaluation.called)
        self.assertRedirects(response, reverse('place_evaluation_list', kwargs={'cohort_id': "cohort"}))
