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
import datetime
import json
from unittest.mock import patch

from django.test import TestCase
from django.core.exceptions import ObjectDoesNotExist

import base.tests.models.test_offer_year
import performance.tests.models.test_student_performance
from performance.models import student_performance as mdl_perf
from performance.queue import student_performance as queue_stud_perf


class TestQueueStudentPerformance(TestCase):
    def setUp(self):
        self.student_performance = performance.tests.models.test_student_performance.create_student_performance()
        self.offer_year = base.tests.models.test_offer_year.create_offer_year()
        self.json_points = performance.tests.models.test_student_performance.load_json_file("performance/tests/ressources/points2.json")
        self.json_points_2 = performance.tests.models.test_student_performance.load_json_file("performance/tests/ressources/points3.json")

    def test_save(self):
        registration_id = self.student_performance.registration_id
        academic_year = self.student_performance.academic_year
        acronym = self.student_performance.acronym
        default_update_date = queue_stud_perf.get_expiration_date(academic_year=academic_year, consumed=True)
        stud_perf = queue_stud_perf.save(registration_id, academic_year, acronym, json.loads(self.json_points),
                                         default_update_date=default_update_date)

        self.student_performance.refresh_from_db()

        self.assertEqual(stud_perf, self.student_performance, "Object should be updated")


        queue_stud_perf.save("4549841", academic_year, acronym, json.loads(self.json_points), default_update_date)
        try:
            mdl_perf.StudentPerformance.objects.get(registration_id="4549841",
                                                    academic_year=self.student_performance.academic_year,
                                                    acronym=self.student_performance.acronym)
        except ObjectDoesNotExist:
            self.fail("Object should be created")

    def test_generate_message(self):
        message = queue_stud_perf.generate_message(self.student_performance.registration_id,
                                                   self.student_performance.academic_year,
                                                   self.student_performance.acronym)
        expected_message = json.dumps({"registration_id": "64641200", "acronym": "SINF2MS/G", "academic_year": "2016"})
        self.assertJSONEqual(message, expected_message, "Wrong message returned.")

    def test_extract_academic_year_from_json(self):
        academic_year = queue_stud_perf.extract_academic_year_from_json(json.loads(self.json_points))
        self.assertEqual(academic_year, 2016, "Invalid academic year")

    def test_extract_acronym_from_json(self):
        acronym = queue_stud_perf.extract_acronym_from_json(json.loads(self.json_points))
        self.assertEqual(acronym, "SINF2MS/G", "Invalid academic year")

    def test_extract_student_from_json(self):
        registration_id = queue_stud_perf.extract_student_from_json(json.loads(self.json_points))
        self.assertEqual(registration_id, "64641200", "Invalid registration id")

    def test_callback(self):
        queue_stud_perf.callback(self.json_points.encode())
        self.student_performance.refresh_from_db()
        self.assertJSONEqual(json.dumps(self.student_performance.data), self.json_points, "Object should be updated")

        queue_stud_perf.callback(self.json_points_2.encode())

        try:
            mdl_perf.StudentPerformance.objects.get(registration_id=self.student_performance.registration_id,
                                                    academic_year=self.student_performance.academic_year,
                                                    acronym=self.student_performance.acronym)
        except ObjectDoesNotExist:
            self.fail("Object should be created")

    @patch('frontoffice.queue.queue_listener.Client.call')
    def test_fetch_and_save(self, mock_client_call):
        mock_client_call.return_value = None
        obj = queue_stud_perf.fetch_and_save(self.student_performance.registration_id,
                                             self.student_performance.academic_year,
                                             self.student_performance.acronym)
        self.assertIsNone(obj, "Should return None")

        mock_client_call.return_value = self.json_points.encode()
        obj = queue_stud_perf.fetch_and_save(self.student_performance.registration_id,
                                             self.student_performance.academic_year,
                                             self.student_performance.acronym)
        self.assertIsNotNone(obj, "Should return a valid student performance object")
        self.assertJSONEqual(json.dumps(obj.data), self.json_points, "Incorrect student points json")
        self.assertEqual(self.student_performance.registration_id, obj.registration_id, "Incorrect student")
        self.assertEqual(self.student_performance.academic_year, obj.academic_year, "Incorrect academic_year")
        self.assertEqual(self.student_performance.acronym, obj.acronym, "Incorrect acronym")


class TestUpdateExpDate(TestCase):

    def get_update_exp_date_json_with_reg_id_as_byte(self):
        return b'{"registrationId": "1111111","academicYear": 2016,"acronym": \
        "DROI1BA","expirationDate": 1485267376419,"forceUpdate": false}'

    def get_update_exp_date_json_without_reg_id_as_byte(self):
        return b'{"academicYear":2016,"acronym":\
        "DROI1BA","expirationDate":1485267376419,"forceUpdate":false}'

    def setUp(self):
        self.student_performance_1 = performance.tests.models.test_student_performance.\
            create_student_performance('DROI1BA', '1111111', 2016, datetime.datetime.now())
        self.student_performance_2 = performance.tests.models.test_student_performance.\
            create_student_performance('DROI1BA', '2222222', 2016, datetime.datetime.now())

    def test_update_with_registration_id(self):
        queue_stud_perf.update_exp_date_callback(self.get_update_exp_date_json_with_reg_id_as_byte())
        student_perf_1 = mdl_perf.find_by_pk(self.student_performance_1.pk)
        student_perf_2 = mdl_perf.find_by_pk(self.student_performance_2.pk)
        self.assertNotEqual(student_perf_1.update_date.replace(microsecond=0),
                            student_perf_2.update_date.replace(microsecond=0))

    def test_update_without_registration_id(self):
        queue_stud_perf.update_exp_date_callback(self.get_update_exp_date_json_without_reg_id_as_byte())
        student_perf_1 = mdl_perf.find_by_pk(self.student_performance_1.pk)
        student_perf_2 = mdl_perf.find_by_pk(self.student_performance_2.pk)
        self.assertEqual(student_perf_1.update_date.replace(microsecond=0),
                         student_perf_2.update_date.replace(microsecond=0))


