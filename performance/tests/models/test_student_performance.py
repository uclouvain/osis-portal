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

from django.test import TestCase

import base.tests.models.test_offer_year
from performance import models as mdl_performance
from performance.models import student_performance as mdl_perf
import datetime
from django.core.exceptions import ObjectDoesNotExist


def create_student_performance(acronym="SINF2MS/G", registration_id="64641200",
                               academic_year=2016, update_date=datetime.datetime.now()):
    with open("performance/tests/ressources/points.json") as f:
        data = json.load(f)
    a_student_performance = mdl_performance.student_performance.StudentPerformance(acronym=acronym,
                                                                                   registration_id=registration_id,
                                                                                   academic_year=academic_year,
                                                                                   update_date=update_date,
                                                                                   data=data)
    a_student_performance.save()
    return a_student_performance


def load_json_file(json_path):
    with open(json_path) as json_file:
        return json_file.read()


class TestModelStudentPerformance(TestCase):
    def setUp(self):
        self.student_performance = create_student_performance()
        self.offer_year = base.tests.models.test_offer_year.create_offer_year()
        self.json_points = load_json_file("performance/tests/ressources/points2.json")

    def test_search(self):
        student_performances = mdl_perf.search(registration_id=self.student_performance.registration_id)
        self.assertIn(self.student_performance, student_performances, "Invalid search result with student as argument")

        student_performances = mdl_perf.search(academic_year=self.student_performance.academic_year)
        self.assertIn(self.student_performance, student_performances,
                      "Invalid search result with academic_year as argument")

        student_performances = mdl_perf.search(acronym=self.student_performance.acronym)
        self.assertIn(self.student_performance, student_performances,
                      "Invalid search result with acronym as argument")

        student_performances = mdl_perf.search(registration_id="541315")
        self.assertFalse(student_performances, "Should return empty result")

    def test_find_by_pk(self):
        actual = mdl_perf.find_by_pk(self.student_performance.pk)
        self.assertEqual(actual, self.student_performance)

    def test_find_by_student_and_offer_year(self):
        actual_student_performance = mdl_perf.find_by_student_and_offer_year(self.student_performance.registration_id,
                                                                             self.student_performance.academic_year,
                                                                             self.student_performance.acronym)
        self.assertEqual(actual_student_performance, self.student_performance)

        actual_student_performance = mdl_perf.find_by_student_and_offer_year("464846",
                                                                             self.student_performance.academic_year,
                                                                             self.student_performance.acronym)
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
        stud_perf = mdl_perf.update_or_create(self.student_performance.registration_id,
                                              self.student_performance.academic_year,
                                              self.student_performance.acronym,
                                              fields_value)

        self.student_performance.refresh_from_db()
        self.assertEqual(stud_perf, self.student_performance, "Object should be updated")

        mdl_perf.update_or_create("489461",
                                  self.student_performance.academic_year,
                                  self.student_performance.acronym,
                                  fields_value)
        try:
            mdl_perf.StudentPerformance.objects.get(registration_id="489461",
                                                    academic_year=self.student_performance.academic_year,
                                                    acronym=self.student_performance.acronym)
        except ObjectDoesNotExist:
            self.fail("Object should be created")



