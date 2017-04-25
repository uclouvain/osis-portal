##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
from unittest import skip
from django.conf import settings
from django.test import TestCase
from mock import patch
from attestation.queues import student_attestation_status as std_att_stat
from attestation.views import main as v_main


class TestFetchSutentAttestationStatuses(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.json_message = v_main._make_registration_json_message('1111111')

    def test_fetch_with_message_none(self):
        attestation_statuses = std_att_stat.fetch_json_attestation_statuses(None)
        self.assertIsNone(attestation_statuses)

    if hasattr(settings, 'QUEUES') and settings.QUEUES:
        @patch('frontoffice.queue.queue_listener.AttestationStatusClient.call')
        def test_fetch_without_result(self, mock_client_call):
            mock_client_call.return_value = None
            attestation_statuses = std_att_stat.fetch_json_attestation_statuses(self.json_message)
            self.assertIsNone(attestation_statuses)

        @patch('frontoffice.queue.queue_listener.Client.call')
        def test_fetch_with_results(self, mock_client_call):
            mock_client_call.return_value = self._get_test_attestation_statuses_as_byte()
            attestation_statuses = std_att_stat.fetch_json_attestation_statuses(self.json_message)
            attesatation_statuses_expected = self._get_test_attestation_statuses_as_dict()
            self.assertDictEqual(attesatation_statuses_expected, attestation_statuses)

    def _get_test_attestation_statuses_as_byte(self):
        return b'{"available": true,"academicYear": 2016,"attestationStatuses": [{"type": "REGISTRATION","printed": true,"available": false},{"type": "STUDENT_CARD","printed": false,"available": false},{"type": "REGULAR_REGISTRATION","printed": true,"available": true}]}'

    def _get_test_attestation_statuses_as_dict(self):
        return {
            'available': True,
            'academicYear': 2016,
            'attestationStatuses': [
                {
                    'type': 'REGISTRATION',
                    'printed': True,
                    'available': False
                },
                {
                    'type': 'STUDENT_CARD',
                    'printed': False,
                    'available': False
                },
                {
                    'type': 'REGULAR_REGISTRATION',
                    'printed': True,
                    'available': True
                }
            ]
        }
