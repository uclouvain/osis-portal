##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2021 Université catholique de Louvain (http://www.uclouvain.be)
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
import datetime

from django.test import TestCase

from attribution.views import students_list
from base.models.enums import learning_unit_year_subtypes
from base.tests.factories.learning_container_year import LearningContainerYearInChargeFactory
from base.tests.factories.learning_unit_enrollment import LearningUnitEnrollmentFactory
from base.tests.factories.tutor import TutorFactory
from base.tests.models import test_academic_year, test_learning_unit_year
from performance.tests.models import test_student_performance
from base.tests.factories.student_specific_profile import StudentSpecificProlileFactory


# TODO: Rewrite test because not lisible!!!
class StudentsListViewTest(TestCase):
    def setUp(self):
        self.current_year = datetime.date.today().year
        self.next_year = datetime.date.today().year + 1

        self.a_tutor = TutorFactory()
        self.full_luy = self.create_lu_yr_annual_data(self.current_year)

    def create_lu_yr_annual_data(self, a_year):
        an_academic_yr = test_academic_year.create_academic_year_with_year(a_year)
        an_academic_yr.year = a_year
        a_container_year = LearningContainerYearInChargeFactory()
        a_learning_unit_year = test_learning_unit_year.create_learning_unit_year({
            'acronym': 'LELEC1530',
            'specific_title': 'Circ. Electro. Analog. & Digit. Fondam.',
            'academic_year': an_academic_yr,
            'weight': 5,
            'subtype': learning_unit_year_subtypes.FULL,
        })
        a_learning_unit_year.learning_container_year = a_container_year
        a_learning_unit_year.save()
        return {
            'academic_year': an_academic_yr,
            'learning_unit_year': a_learning_unit_year,
        }

    def test_find_january_note(self):
        student_performance = test_student_performance.create_student_performance()
        an_academic_yr = test_academic_year.create_academic_year_with_year(student_performance.academic_year)
        a_learning_unit_year = test_learning_unit_year.create_learning_unit_year({
            'acronym': 'LINGI2145',
            'specific_title': 'DummyTitle',
            'academic_year': an_academic_yr,
            'weight': 5
        })
        self.assertEqual(
            students_list.get_sessions_results(
                student_performance.registration_id, a_learning_unit_year, student_performance.acronym), {
                    students_list.JANUARY: {
                         students_list.JSON_LEARNING_UNIT_NOTE: '13.0',
                         students_list.JSON_LEARNING_UNIT_STATUS: 'I'
                     },
                    students_list.JUNE: {
                         students_list.JSON_LEARNING_UNIT_NOTE: '13.0',
                         students_list.JSON_LEARNING_UNIT_STATUS: 'R'
                    },
                    students_list.SEPTEMBER: {
                         students_list.JSON_LEARNING_UNIT_NOTE: '-',
                         students_list.JSON_LEARNING_UNIT_STATUS: '-'
                    }
                }
        )

    def test_get_student_performance_data_dict(self):
        student_performance = test_student_performance.create_student_performance()
        self.assertEqual(students_list.get_student_data_dict(student_performance), student_performance.data)

    def test_get_no_student_performance_data_dict(self):
        self.assertIsNone(students_list.get_student_data_dict(None))

    def test_get_learning_unit_enrollments_list(self):
        luy_full = self.full_luy['learning_unit_year']
        luy_partim = test_learning_unit_year.create_learning_unit_year({
            'acronym': "{}A".format('LINGI2145'),
            'specific_title': 'Dummy title',
            'academic_year': self.full_luy['academic_year'],
            'weight': 5,
            'subtype': learning_unit_year_subtypes.PARTIM,
        })
        luy_partim.learning_container_year = luy_full.learning_container_year
        luy_partim.save()
        for _ in range(5):
            LearningUnitEnrollmentFactory(learning_unit_year=luy_full)
            LearningUnitEnrollmentFactory(learning_unit_year=luy_partim)

        self.assertEqual(
            len(students_list._get_learning_unit_yr_enrollments_list(luy_full)),
            10
        )

    def test_has_no_peps(self):
        self.assertFalse((students_list.check_peps(self.full_luy['learning_unit_year'].acronym,
                                                   self.full_luy['academic_year'].year)))

    def test_has_peps(self):
        student_peps = StudentSpecificProlileFactory()
        enrollment = LearningUnitEnrollmentFactory(offer_enrollment__student=student_peps.student)
        self.assertTrue(students_list.check_peps(enrollment.learning_unit_year.acronym,
                                                 enrollment.learning_unit_year.academic_year.year))
