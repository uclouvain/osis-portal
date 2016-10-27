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
from admission.tests import data_for_tests
from performance.models import student_performance as mdl_perf
import json
import datetime
from django.core.exceptions import ObjectDoesNotExist


class TestStudentPerformance(TestCase):
    def setUp(self):
        self.student_performance = data_for_tests.create_student_performance()
        with open("performance/tests/ressources/points.json") as json_file:
            self.json_points = json.load(json_file)

    def test_update_or_create(self):
        fields_value = {"data": self.json_points, "update_date": datetime.date.today()}
        student = self.student_performance.student
        offer_year = self.student_performance.offer_year
        stud_perf = mdl_perf.update_or_create(student, offer_year, fields_value)

        self.assertDictEqual(stud_perf.data, self.json_points, "Object should be updated")

        other_student = data_for_tests.create_student_with_specific_registration_id("64641202")
        mdl_perf.update_or_create(other_student, offer_year, fields_value)
        try:
            mdl_perf.StudentPerformance.objects.get(student=other_student, offer_year=offer_year)
        except ObjectDoesNotExist:
            self.fail("Object should be created")

    def test_has_expired(self):
        timedelta = datetime.timedelta(days=4)

        self.assertFalse(mdl_perf.has_expired(self.student_performance))

        self.student_performance.update_date = datetime.date.today() + timedelta
        self.assertFalse(mdl_perf.has_expired(self.student_performance))

        self.student_performance.update_date = datetime.date.today() - timedelta
        self.assertTrue(mdl_perf.has_expired(self.student_performance))

    def test_find_by_student_and_offer_year(self):
        student = self.student_performance.student
        offer_year = self.student_performance.offer_year
        stud_perf = mdl_perf.find_by_student_and_offer_year(student, offer_year)
        self.assertEqual(stud_perf, self.student_performance, "Don\"t return the correct object")

        other_student = data_for_tests.create_student_with_specific_registration_id("64641202")
        stud_perf = mdl_perf.find_by_student_and_offer_year(other_student, offer_year)
        self.assertIsNone(stud_perf, "Should find nothing")

