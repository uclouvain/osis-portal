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
import json
import datetime
from django.test import TestCase
from attestation.queues import student_attestation_status as std_att_stat
from base.models import student as mdl_student, person as mdl_person
from attestation.models.enums import attestation_type
from attestation.models import attestation_status as mdl_attest_stat


class TestRegistartionIdMessage(TestCase):

    def test_generate_message_with_registration_id(self):
        given_json_message = std_att_stat._generate_registration_id_message('1111111')
        expected_json_message = json.loads('{"registration_id" : "1111111"}')
        self.assertJSONEqual(given_json_message, expected_json_message)

    def test_generate_message_without_registration_id(self):
        given_json_message = std_att_stat._generate_registration_id_message(None)
        self.assertIsNone(given_json_message)


class TestSaveDataFromJson(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.person = mdl_person.Person(last_name='user_1', global_id='1111111')
        cls.student = mdl_student.Student(person=cls.person, registration_id='11111111')

    def test_save_data_from_json(self):
        json_data_as_byte = b'{"attestation_statuses": [ ' \
                            b'{"registration_id": "11111111", "attestation_type": "REGISTRATION", "printed": true, "available": true},' \
                            b'{"registration_id": "11111111", "attestation_type": "STUDENT_CARD", "printed": false, "available": false},' \
                            b'{"registration_id": "11111111", "attestation_type": "REGULAR_REGISTRATION", "printed": false, "available": true}' \
                            b']'

        attestation_statuses = std_att_stat._save_data_from_json(self.student, json.loads(json_data_as_byte.decode("utf-8")))
        self.assertIsNotNone(attestation_statuses)
        self._make_status_assertion(attestation_statuses[0], '11111111', attestation_type.REGISTRATION, True, True)
        self._make_status_assertion(attestation_statuses[1], '11111111', attestation_type.STUDENT_CARD, False, False)
        self._make_status_assertion(attestation_statuses[2], '11111111', attestation_type.REGULAR_REGISTRATION, False, True)

    def _make_status_assertion(self, attestation_status, registration_id, attest_type, printed, available):
        self.assertEquals(attestation_status.student.registration_id, registration_id)
        self.assertEquals(attestation_status.attestation_type, attest_type)
        self.assertEquals(attestation_status.printed, printed)
        self.assertEquals(attestation_status.available, available)


class TestUpdateDate(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.person = mdl_person.Person(last_name='user_1', global_id='1111111')
        cls.student = mdl_student.Student(person=cls.person, registration_id='11111111')
        now = datetime.datetime.now()
        tomorrow = now + datetime.timedelta(days=1)
        yesterday = now - datetime.timedelta(days=1)
        cls.attestation_status_new = mdl_attest_stat.AttestationStatus(student=cls.student,
                                                                       attestation_type=attestation_type.REGISTRATION,
                                                                       printed=True,
                                                                       available=True,
                                                                       update_date=tomorrow)
        cls.attestation_status_old = mdl_attest_stat.AttestationStatus(student=cls.student,
                                                                       attestation_type=attestation_type.STUDENT_CARD,
                                                                       printed=True,
                                                                       available=True,
                                                                       update_date=yesterday)

    def test_has_not_to_be_updated(self):
        self.assertFalse(std_att_stat._has_to_be_updated(self.attestation_status_new))

    def test_has_to_be_updated(self):
        self.assertTrue(std_att_stat._has_to_be_updated(self.attestation_status_old))
