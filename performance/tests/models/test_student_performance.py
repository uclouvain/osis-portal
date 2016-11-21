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
from performance.tests import data_for_tests as utility_data
from performance.models import student_performance as mdl_perf
import datetime
from django.core.exceptions import ObjectDoesNotExist


class TestModelStudentPerformance(TestCase):
    def setUp(self):
        self.student_performance = data_for_tests.create_student_performance()
        self.offer_year = \
            data_for_tests.create_offer_year_with_academic_year(self.student_performance.offer_year.academic_year)
        self.json_points = utility_data.load_json_file("performance/tests/ressources/points2.json")

    def test_search(self):
        student_performances = mdl_perf.search(student=self.student_performance.student)
        self.assertIn(self.student_performance, student_performances, "Invalid search result with student as argument")

        student_performances = mdl_perf.search(offer_year=self.student_performance.offer_year)
        self.assertIn(self.student_performance, student_performances,
                      "Invalid search result with offer_year as argument")

        other_student = self.create_other_student()
        student_performances = mdl_perf.search(student=other_student)
        self.assertFalse(student_performances, "Should return empty result")

    def test_find_by_student_and_offer_year(self):
        actual_student_performance = mdl_perf.find_by_student_and_offer_year(self.student_performance.student,
                                                                             self.student_performance.offer_year)
        self.assertEqual(actual_student_performance, self.student_performance)

        other_student = self.create_other_student()
        actual_student_performance = mdl_perf.find_by_student_and_offer_year(other_student,
                                                                             self.student_performance.offer_year)
        self.assertNotEqual(actual_student_performance, self.student_performance)

    def test_has_expired(self):
        expired_date = datetime.datetime.strptime("January 20 2000 5:30", "%B %d %Y %H:%M")
        self.student_performance.update_date = expired_date
        self.assertTrue(self.student_performance, "Should return true as date of update has been exceeded")

        not_expired_date = datetime.datetime.strptime("January 20 2099 5:30", "%B %d %Y %H:%M")
        self.student_performance.update_date = not_expired_date
        self.assertTrue(self.student_performance, "Should return false as date of update has not been exceeded")

    def test_update_or_create(self):
        fields_value = {"data": self.json_points, "update_date": datetime.date.today()}
        student = self.student_performance.student
        offer_year = self.student_performance.offer_year
        stud_perf = mdl_perf.update_or_create(student, offer_year, fields_value)

        self.student_performance.refresh_from_db()
        self.assertEqual(stud_perf, self.student_performance, "Object should be updated")

        other_student = data_for_tests.create_student_with_specific_registration_id("64641202")
        mdl_perf.update_or_create(other_student, offer_year, fields_value)
        try:
            mdl_perf.StudentPerformance.objects.get(student=other_student, offer_year=offer_year)
        except ObjectDoesNotExist:
            self.fail("Object should be created")

    @staticmethod
    def create_other_student():
        return data_for_tests.create_student("5621231")