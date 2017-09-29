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
from unittest.mock import patch

from django.conf import settings
from django.contrib.auth.models import Group, Permission
from django.core.urlresolvers import reverse
from django.test import TestCase, Client, modify_settings, override_settings
from django.utils.translation import ugettext_lazy as _

from assessments.tests.factories.score_encoding import ScoreEncodingFactory
from assessments.tests.models import test_score_encoding
from assessments.views import score_encoding
from base.tests.factories.person import PersonFactory
from base.tests.factories.tutor import TutorFactory


GLOBAL_ID = "45451200"
OTHER_GLOBAL_ID = "92921100"
OK = 200
BAD_REQUEST = 400
ACCESS_DENIED = 401
FILE_NOT_FOUND = 404
METHOD_NOT_ALLOWED = 405


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

    def test_when_request_is_post(self):
        response = self.client.post(self.url, data={}, follow=True)
        self.assertEqual(response.status_code, METHOD_NOT_ALLOWED)

    def test_when_request_is_not_ajax(self):
        response = self.client.get(self.url, data={}, follow=True)
        self.assertEqual(response.status_code, ACCESS_DENIED)

    @modify_settings(INSTALLED_APPS={'remove': 'assessments'})
    def test_when_app_not_installed(self):
        response = self.client.get(self.url, data={}, follow=True, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, METHOD_NOT_ALLOWED)

    def test_when_no_corresponding_papersheet(self):
        response = self.client.get(self.url, data={}, follow=True, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, FILE_NOT_FOUND)

    def test_when_papersheet_is_present(self):
        ScoreEncodingFactory(global_id=GLOBAL_ID)

        response = self.client.get(self.url, data={}, follow=True, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, OK)


class AskPaperSheetTest(TestCase):
    def setUp(self):
        a_person = PersonFactory(global_id=GLOBAL_ID)

        tutors_group = Group.objects.create(name='tutors')
        permission = Permission.objects.get(codename="is_tutor")
        tutors_group.permissions.add(permission)
        a_person.user.groups.add(tutors_group)

        self.tutor = TutorFactory(person=a_person)

        self.client = Client()
        self.url = reverse('ask_papersheet', args=[GLOBAL_ID])
        self.client.force_login(a_person.user)

    def test_when_no_tutor(self):
        self.tutor.delete()

        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, ACCESS_DENIED)

    def test_when_request_is_post(self):
        response = self.client.post(self.url, data={}, follow=True)
        self.assertEqual(response.status_code, METHOD_NOT_ALLOWED)

    def test_when_request_is_not_ajax(self):
        response = self.client.get(self.url, data={}, follow=True)
        self.assertEqual(response.status_code, ACCESS_DENIED)

    @modify_settings(INSTALLED_APPS={'remove': 'assessments'})
    def test_when_app_not_installed(self):
        response = self.client.get(self.url, data={}, follow=True, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, METHOD_NOT_ALLOWED)

    @override_settings(QUEUES="")
    def test_when_no_queues(self):
        response = self.client.get(self.url, data={}, follow=True, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, METHOD_NOT_ALLOWED)

    if hasattr(settings, 'QUEUES') and settings.QUEUES:
        @patch('assessments.views.score_encoding.ask_queue_for_papersheet')
        def test_when_exception_occured_when_publishing_to_queue(self, mock_ask_queue_for_papersheet):
            from pika.exceptions import ConnectionClosed, ChannelClosed, AMQPError
            side_effects = [RuntimeError, ConnectionClosed, ChannelClosed, AMQPError]

            for side_effect in side_effects:
                mock_ask_queue_for_papersheet.side_effect = side_effect

                response = self.client.get(self.url, data={}, follow=True, HTTP_X_REQUESTED_WITH='XMLHttpRequest')

                self.assertTrue(mock_ask_queue_for_papersheet.called)
                self.assertEqual(response.status_code, BAD_REQUEST)

        @patch('assessments.views.score_encoding.ask_queue_for_papersheet', side_effect=lambda x: False)
        def test_when_message_not_publish_to_queue(self, mock_ask_queue_for_papersheet):
            response = self.client.get(self.url, data={}, follow=True, HTTP_X_REQUESTED_WITH='XMLHttpRequest')

            self.assertTrue(mock_ask_queue_for_papersheet.called)
            self.assertEqual(response.status_code, METHOD_NOT_ALLOWED)

        @patch('assessments.views.score_encoding.ask_queue_for_papersheet', side_effect=lambda x: True)
        def test_when_message_publish_to_queue(self, mock_ask_queue_for_papersheet):
            response = self.client.get(self.url, data={}, follow=True, HTTP_X_REQUESTED_WITH='XMLHttpRequest')

            self.assertTrue(mock_ask_queue_for_papersheet.called)
            self.assertEqual(response.status_code, OK)


class DownloadPaperSheetTest(TestCase):
    def setUp(self):
        a_person = PersonFactory(global_id=GLOBAL_ID)

        tutors_group = Group.objects.create(name='tutors')
        permission = Permission.objects.get(codename="is_tutor")
        tutors_group.permissions.add(permission)
        a_person.user.groups.add(tutors_group)

        self.tutor = TutorFactory(person=a_person)

        self.client = Client()
        self.url = reverse('scores_download', args=[GLOBAL_ID])
        self.client.force_login(a_person.user)

    def test_when_user_not_tutor(self):
        self.tutor.delete()

        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, ACCESS_DENIED)

    def test_when_trying_to_access_other_tutor_papersheet(self):
        self.url = reverse('scores_download', args=[OTHER_GLOBAL_ID])
        response = self.client.get(self.url, follow=True)

        self.assertEqual(response.status_code, ACCESS_DENIED)

    def test_when_papersheet_is_not_present(self):
        response = self.client.get(self.url, follow=True)

        self.assertEqual(response.context['scores_sheets_unavailable'], True)
        self.assertTemplateUsed(response, 'scores_sheets.html')

    def test_when_papersheet_is_present(self):
        ScoreEncodingFactory(global_id=GLOBAL_ID)

        response = self.client.get(self.url, follow=True)

        self.assertEqual(response.status_code, OK)
        self.assertEqual(response.get('Content-Type'),
                         'application/pdf')
        self.assertEqual(response.get('Content-Disposition'),
                         'attachment; filename="%s"' % ("%s.pdf" % _('scores_sheet')))

    def test_when_person_not_exist_as_faculty_administrator(self):
        self.__set_user_as_faculty_administrator()

        response = self.client.get(self.url, follow=True)

        self.assertEqual(response.status_code, FILE_NOT_FOUND)

    def test_when_person_exists_but_no_papersheet_as_faculty_adminstrator(self):
        PersonFactory(global_id=OTHER_GLOBAL_ID)

        self.__set_user_as_faculty_administrator()

        response = self.client.get(self.url, follow=True)

        self.assertEqual(response.context['scores_sheets_unavailable'], True)
        self.assertTemplateUsed(response, 'scores_sheets.html')

    def test_when_faculty_administator(self):
        PersonFactory(global_id=OTHER_GLOBAL_ID)
        ScoreEncodingFactory(global_id=OTHER_GLOBAL_ID)

        self.__set_user_as_faculty_administrator()

        response = self.client.get(self.url, follow=True)

        self.assertEqual(response.status_code, OK)
        self.assertEqual(response.get('Content-Type'),
                         'application/pdf')
        self.assertEqual(response.get('Content-Disposition'),
                         'attachment; filename="%s"' % ("%s.pdf" % _('scores_sheet')))

    def __set_user_as_faculty_administrator(self):
        faculty_admin_permission = Permission.objects.get(codename="is_faculty_administrator")
        self.tutor.person.user.user_permissions.add(faculty_admin_permission)
        self.url = reverse('scores_download', args=[OTHER_GLOBAL_ID])


class ScoreSheetTest(TestCase):
    def setUp(self):
        self.score_encoding = ScoreEncodingFactory(global_id=GLOBAL_ID)

    def test_get_score_sheet_invalid_json(self):
        global_id = "007896"
        test_score_encoding.create_invalid_score_encoding(global_id=global_id)
        document = score_encoding.get_score_sheet(global_id)
        self.assertIsNone(document)

    def test_check_db_scores(self):
        scores_check = score_encoding.check_db_scores(GLOBAL_ID)
        self.assertTrue(scores_check)

    def test_get_score_sheet_if_not_present_in_db(self):
        self.score_encoding.delete()

        document = score_encoding.get_score_sheet(GLOBAL_ID)
        self.assertIsNone(document)

    def test_get_score_sheet_if_present_in_db_but_outdated(self):
        old_date = "15/11/2016"
        json_obj = json.loads(self.score_encoding.document)
        json_obj['publication_date'] = old_date
        self.score_encoding.document = json.dumps(json_obj)
        self.score_encoding.save()

        document = score_encoding.get_score_sheet(GLOBAL_ID)
        self.assertIsNone(document)

    def test_get_score_sheet_if_present_in_db(self):
        document = score_encoding.get_score_sheet(GLOBAL_ID)
        self.assertJSONEqual(self.score_encoding.document, document)


class PrintScoreSheetTest(TestCase):
    def setUp(self):
        self.score_encoding = ScoreEncodingFactory(global_id=GLOBAL_ID)

    def test_when_no_scores_sheet(self):
        pdf = score_encoding.print_scores("014")
        self.assertIsNone(pdf, "Should not create any pdf")

    def test_when_scores_sheet(self):
        pdf = score_encoding.print_scores(GLOBAL_ID)
        self.assertTrue(pdf, "Should generate a pdf")

    def test_when_invalid_json(self):
        global_id = "007896"
        test_score_encoding.create_invalid_score_encoding(global_id=global_id)
        pdf = score_encoding.print_scores(global_id)
        self.assertIsNone(pdf, "Should not create any pdf")
