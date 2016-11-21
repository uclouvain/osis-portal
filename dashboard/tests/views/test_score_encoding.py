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
from django.test import TestCase
from dashboard.tests import data_for_tests
from dashboard.views import score_encoding
from unittest.mock import patch


class ScoreSheetTest(TestCase):
    def setUp(self):
        self.score_encoding = data_for_tests.create_score_encoding()
        self.global_id = self.score_encoding.global_id

    def test_get_score_sheet_if_present_in_db(self):
        document = score_encoding.get_score_sheet(self.global_id)
        self.assertJSONEqual(self.score_encoding.document, document, "Should return the document in db")

    @patch('frontoffice.queue.queue_listener.Client.call')
    def test_get_score_sheet_if_present_in_db_but_outdated(self, mock_client_call):
        global_id = "12012"
        new_score_encoding = data_for_tests.create_score_encoding(global_id=global_id)
        new_score_encoding.document = data_for_tests.get_old_sample()
        new_score_encoding.save()

        expected = data_for_tests.get_sample()
        mock_client_call.return_value = expected.encode("utf-8")
        document = score_encoding.get_score_sheet(global_id)
        self.assertJSONEqual(document, expected, "Should fetch document from queue")

    @patch('frontoffice.queue.queue_listener.Client.call')
    def test_get_score_sheet_if_not_present_in_db_with_timeout(self, mock_client_call):
        mock_client_call.return_value = None
        document = score_encoding.get_score_sheet("12012")
        self.assertIsNone(document, "Should timeout when waiting for document and return none")

    @patch('frontoffice.queue.queue_listener.Client.call')
    def test_get_score_sheet_if_not_present_in_db_and_fetch(self, mock_client_call):
        expected = data_for_tests.get_sample()
        mock_client_call.return_value = expected.encode("utf-8")
        document = score_encoding.get_score_sheet("12012")
        self.assertJSONEqual(document, expected, "Should fetch document from queue")


class PrintScoreSheetTest(TestCase):
    def setUp(self):
        self.score_encoding = data_for_tests.create_score_encoding()
        self.global_id = self.score_encoding.global_id

    def test_when_no_scores_sheet(self):
        pdf = score_encoding.print_scores(None, "014")
        self.assertIsNone(pdf, "Should not create any pdf")

    def test_when_scores_sheet(self):
        pdf = score_encoding.print_scores(None, self.global_id)
        self.assertTrue(pdf, "Should generate a pdf")



