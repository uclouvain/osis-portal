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

import base.tests.models.test_offer_year
import base.tests.models.test_student
import performance.tests.models.test_student_performance
from performance.views import main


class TestMain(TestCase):
    def setUp(self):
        self.student_performance = performance.tests.models.test_student_performance.create_student_performance()
        self.offer_year = base.tests.models.test_offer_year.create_offer_year()
        self.json_points = performance.tests.models.test_student_performance.load_json_file("performance/tests/ressources/points2.json")
        self.json_points_2 = performance.tests.models.test_student_performance.load_json_file("performance/tests/ressources/points3.json")

    def test_convert_student_performance_to_dic(self):
        student_performance_dic = main.convert_student_performance_to_dic(self.student_performance)
        expected = {"academic_year": 2016,
                    "acronym": "SINF2MS/G",
                    "title": " Master [120] en sciences informatiques, à finalité spécialisée ",
                    "pk": self.student_performance.pk}
        self.assertDictEqual(student_performance_dic, expected)

    def test_check_right_access(self):
        student = base.tests.models.test_student.create_student(self.student_performance.registration_id)
        has_access = main.check_right_access(self.student_performance, student)
        self.assertTrue(has_access)

        student = base.tests.models.test_student.create_student(registration_id="879466")
        has_access = main.check_right_access(self.student_performance, student)
        self.assertFalse(has_access)


