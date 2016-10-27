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
import json
from performance.models import student_performance as mdl_perf
from performance.queue import student_performance as queue_stud_perf
from django.core.exceptions import ObjectDoesNotExist


class TestQueueStudentPerformance(TestCase):
    def setUp(self):
        self.student_performance = data_for_tests.create_student_performance()
        with open("performance/tests/ressources/points.json") as json_file:
            self.json_points = json.load(json_file)

    def test_save(self):
        student = self.student_performance.student
        offer_year = self.student_performance.offer_year
        stud_perf = queue_stud_perf.save(student, offer_year, self.json_points)

        self.assertDictEqual(stud_perf.data, self.json_points, "Object should be updated")

        other_student = data_for_tests.create_student_with_specific_registration_id("64641202")
        queue_stud_perf.save(other_student, offer_year, self.json_points)
        try:
            mdl_perf.StudentPerformance.objects.get(student=other_student, offer_year=offer_year)
        except ObjectDoesNotExist:
            self.fail("Object should be created")


