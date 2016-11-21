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
from performance.queue import student_performance as queue_stud_perf
from django.core.exceptions import ObjectDoesNotExist


class TestQueueStudentPerformance(TestCase):
    def setUp(self):
        self.student_performance = data_for_tests.create_student_performance()
        self.offer_year = \
            data_for_tests.create_offer_year_with_academic_year(self.student_performance.offer_year.academic_year)
        self.json_points = utility_data.load_json_file("performance/tests/ressources/points2.json")
        self.json_points_2 = utility_data.load_json_file("performance/tests/ressources/points3.json")

    def test_save(self):
        student = self.student_performance.student
        offer_year = self.student_performance.offer_year
        stud_perf = queue_stud_perf.save(student, offer_year, self.json_points)

        self.student_performance.refresh_from_db()

        self.assertEqual(stud_perf, self.student_performance, "Object should be updated")

        other_student = data_for_tests.create_student_with_specific_registration_id("64641202")
        queue_stud_perf.save(other_student, offer_year, self.json_points)
        try:
            mdl_perf.StudentPerformance.objects.get(student=other_student, offer_year=offer_year)
        except ObjectDoesNotExist:
            self.fail("Object should be created")

    def test_callback(self):
        queue_stud_perf.callback(self.json_points)
        self.student_performance.refresh_from_db()

        self.assertDictEqual(self.student_performance.data, self.json_points, "Object should be updated")

        queue_stud_perf.callback(self.json_points_2)

        try:
            mdl_perf.StudentPerformance.objects.get(student=self.student_performance.student,
                                                    offer_year=self.offer_year)
        except ObjectDoesNotExist:
            self.fail("Object should be created")




