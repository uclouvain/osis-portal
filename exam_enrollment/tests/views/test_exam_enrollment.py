##############################################################################
#
# OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2018 Université catholique de Louvain (http://www.uclouvain.be)
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

from base.models.enums import offer_enrollment_state
from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.group import GroupFactory
from base.tests.factories.offer_enrollment import OfferEnrollmentFactory
from base.tests.factories.offer_year import OfferYearFactory
from base.tests.factories.student import StudentFactory
from exam_enrollment.views import exam_enrollment


class TestExamEnrollment(TestCase):
    @classmethod
    def setUpTestData(cls):
        GroupFactory(name='students')
        cls.academic_year = AcademicYearFactory()
        cls.off_year = OfferYearFactory(academic_year=cls.academic_year)
        cls.student = StudentFactory()

    def test_get_student_programs(self):
        OfferEnrollmentFactory(student=self.student, offer_year=self.off_year,
                               enrollment_state=offer_enrollment_state.PROVISORY)
        OfferEnrollmentFactory(student=self.student, offer_year=self.off_year,
                               enrollment_state=offer_enrollment_state.SUBSCRIBED)
        OfferEnrollmentFactory(student=self.student, offer_year=self.off_year, enrollment_state=None)
        enrollments = exam_enrollment._get_student_programs(self.student, self.academic_year)
        self.assertEqual(len(enrollments), 2)
