##############################################################################
#
# OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2017 Université catholique de Louvain (http://www.uclouvain.be)
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

from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.offer_enrollment import OfferEnrollmentFactory
from base.tests.factories.offer_year import OfferYearFactory
from base.tests.factories.student import StudentFactory
from base.models.enums import offer_enrollment_state
from django.contrib.auth.models import Group
from exam_enrollment.views import exam_enrollment


class TestExamEnrollment(TestCase):

    def setUp(self):
        Group(name='students').save()

    def test_get_student_programs(self):
        academic_year = AcademicYearFactory()
        off_year = OfferYearFactory(academic_year=academic_year)
        student = StudentFactory()
        OfferEnrollmentFactory(student=student, offer_year=off_year, enrollment_state=offer_enrollment_state.PROVISORY)
        OfferEnrollmentFactory(student=student, offer_year=off_year, enrollment_state=offer_enrollment_state.SUBSCRIBED)
        OfferEnrollmentFactory(student=student, offer_year=off_year, enrollment_state=None)
        enrollments = exam_enrollment._get_student_programs(student, academic_year)
        self.assertEqual(len(enrollments), 2)
