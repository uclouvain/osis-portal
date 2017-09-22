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
from django.conf import settings
from django.contrib.auth.models import Group, Permission
from django.core.urlresolvers import reverse
from django.test import TestCase, Client
from unittest.mock import patch

from assessments.tests.models import test_score_encoding
from assessments.tests.factories.score_encoding import ScoreEncodingFactory
from assessments.views import score_encoding
from base.models.tutor import Tutor
from base.tests.factories.person import PersonFactory
from base.tests.factories.tutor import TutorFactory


GLOBAL_ID = "45451200"
ACCESS_DENIED = 401
METHOD_NOT_ALLOWED = 405
FILE_NOT_FOUND = 404
OK = 200


class CheckPaperSheetTest(TestCase):
    def setUp(self):
        a_person = PersonFactory(global_id=GLOBAL_ID)

        tutors_group = Group.objects.create(name='tutors')
        permission = Permission.objects.get(codename="is_tutor")
        tutors_group.permissions.add(permission)
        a_person.user.groups.add(tutors_group)

        self.tutor = TutorFactory(person=a_person)

        self.client = Client()
        self.url = reverse('check_papersheet', args=[GLOBAL_ID])
        self.client.force_login(a_person.user)

    def test_when_no_tutor(self):
        self.tutor.delete()

        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, ACCESS_DENIED)

    def test_when_request_is_get(self):
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, METHOD_NOT_ALLOWED)

    def test_when_request_is_not_ajax(self):
        response = self.client.post(self.url, data={}, follow=True)
        self.assertEqual(response.status_code, ACCESS_DENIED)

    def test_when_app_not_installed(self):
        with self.modify_settings(INSTALLED_APPS={'remove': 'assessments'}):
            response = self.client.post(self.url, data={}, follow=True, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
            self.assertEqual(response.status_code, METHOD_NOT_ALLOWED)

    def test_when_no_corresponding_papersheet(self):
        response = self.client.post(self.url, data={}, follow=True, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, FILE_NOT_FOUND)

    def test_when_papersheet_is_present(self):
        ScoreEncodingFactory(global_id=GLOBAL_ID)

        response = self.client.post(self.url, data={}, follow=True, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, OK)


class ScoreSheetTest(TestCase):
    def setUp(self):
        self.score_encoding = test_score_encoding.create_score_encoding()
        self.global_id = self.score_encoding.global_id

    def test_get_score_sheet_if_present_in_db(self):
        document = score_encoding.get_score_sheet(self.global_id)
        self.assertJSONEqual(self.score_encoding.document, document, "Should return the document in db")

    def test_check_db_scores(self):
        scores_check = score_encoding.check_db_scores(self.global_id)
        self.assertTrue(scores_check)

    if hasattr(settings, 'QUEUES') and settings.QUEUES:
        @patch('frontoffice.queue.queue_listener.Client.call')
        def test_get_score_sheet_if_present_in_db_but_outdated(self, mock_client_call):
            global_id = "12012"
            new_score_encoding = test_score_encoding.create_score_encoding(global_id=global_id)
            new_score_encoding.document = test_score_encoding.get_old_sample()
            new_score_encoding.save()

            expected = test_score_encoding.get_sample()
            mock_client_call.return_value = expected.encode("utf-8")
            document = score_encoding.get_score_sheet(global_id)
            self.assertIsNone(document)

        @patch('frontoffice.queue.queue_listener.Client.call')
        def test_get_score_sheet_if_not_present_in_db_with_timeout(self, mock_client_call):
            mock_client_call.return_value = None
            document = score_encoding.get_score_sheet("12012")
            self.assertIsNone(document, "Should timeout when waiting for document and return none")

        @patch('frontoffice.queue.queue_listener.Client.call')
        def test_get_score_sheet_if_not_present_in_db_and_fetch(self, mock_client_call):
            expected = test_score_encoding.get_sample()
            mock_client_call.return_value = expected.encode("utf-8")
            document = score_encoding.get_score_sheet("12012")
            self.assertIsNone(document)


class PrintScoreSheetTest(TestCase):
    def setUp(self):
        self.score_encoding = test_score_encoding.create_score_encoding()
        self.global_id = self.score_encoding.global_id

    def test_when_no_scores_sheet(self):
        pdf = score_encoding.print_scores("014")
        self.assertIsNone(pdf, "Should not create any pdf")

    def test_when_scores_sheet(self):
        pdf = score_encoding.print_scores(self.global_id)
        self.assertTrue(pdf, "Should generate a pdf")



