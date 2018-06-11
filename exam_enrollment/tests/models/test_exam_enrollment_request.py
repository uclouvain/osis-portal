##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
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
from django.db import IntegrityError

from base.tests.factories.student import StudentFactory
from exam_enrollment.tests.factories.exam_enrollment_request import ExamEnrollmentRequestFactory


class TestExamEnrollmentRequest(TestCase):

    def test_must_be_unique(self):
        the_student = StudentFactory()
        acronym = 'ACRO0001'

        ExamEnrollmentRequestFactory(student=the_student, offer_year_acronym=acronym)
        with self.assertRaises(IntegrityError):
            ExamEnrollmentRequestFactory(student=the_student, offer_year_acronym=acronym)

    def test_offer_year_acronym_mandatory(self):
        with self.assertRaises(IntegrityError):
            ExamEnrollmentRequestFactory(offer_year_acronym=None)
