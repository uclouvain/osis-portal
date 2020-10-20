#############################################################################
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
from django.contrib.auth.models import Group
from django.core.exceptions import MultipleObjectsReturned
from django.test import TestCase

from base.models.enums import offer_enrollment_state
from base.models.offer_enrollment import OfferEnrollment
from base.models.student import Student
from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.education_group_year import EducationGroupYearFactory
from base.tests.factories.offer_enrollment import OfferEnrollmentFactory
from base.tests.factories.person import PersonFactory
from base.tests.factories.student import StudentFactory
from base.business import student as student_bsn
from base.tests.factories.user import UserFactory


class TestPersonIsStudent(TestCase):
    def setUp(self):
        Group.objects.create(name='students')
        self.person = PersonFactory()
        self.student = StudentFactory(person=self.person)

    def test_check_is_student_with_one_student(self):
        self.assertTrue(student_bsn.check_if_person_is_student(self.person))

    def test_check_is_student_with_more_than_one_student(self):
        StudentFactory(person=self.person)
        StudentFactory(person=self.person)

        self.assertTrue(Student.objects.filter(person=self.person).count() > 1)
        self.assertTrue(student_bsn.check_if_person_is_student(self.person))

    def test_check_is_not_student(self):
        person_not_student = PersonFactory()
        self.assertFalse(student_bsn.check_if_person_is_student(person_not_student))


class TestFindAndDiscriminate(TestCase):
    def setUp(self):
        Group.objects.create(name='students')
        self.user = UserFactory()
        self.person = PersonFactory(user=self.user)
        self.student = StudentFactory(person=self.person)

    def test_one_student(self):
        self.assertEqual(self.student, student_bsn.find_by_user_and_discriminate(self.user))

    def test_no_student(self):
        another_user = UserFactory()
        PersonFactory(user=another_user)
        self.assertIsNone(student_bsn.find_by_user_and_discriminate(another_user))

    def test_one_offer_enrollment_valid(self):
        valid_student = StudentFactory(person=self.person)
        current_academic_year = AcademicYearFactory(year=2020)
        current_education_group_year = EducationGroupYearFactory(academic_year=current_academic_year)
        OfferEnrollmentFactory(student=valid_student, enrollment_state=offer_enrollment_state.PROVISORY,
                               education_group_year=current_education_group_year)
        OfferEnrollmentFactory(student=self.student, enrollment_state=None,
                               education_group_year=current_education_group_year)
        self.assertEqual(student_bsn.find_by_user_and_discriminate(self.user), valid_student)

    def test_last_offer_enrollment_valid(self):
        current_student = StudentFactory(person=self.person)
        current_academic_year = AcademicYearFactory(year=2020)
        previous_academic_year = AcademicYearFactory(year=2019)
        current_education_group_year = EducationGroupYearFactory(academic_year=current_academic_year)
        previous_education_group_year = EducationGroupYearFactory(academic_year=previous_academic_year)
        OfferEnrollmentFactory(student=current_student, enrollment_state=offer_enrollment_state.SUBSCRIBED,
                               education_group_year=current_education_group_year)
        OfferEnrollmentFactory(student=self.student, enrollment_state=offer_enrollment_state.SUBSCRIBED,
                               education_group_year=previous_education_group_year)
        self.assertTrue(Student.objects.filter(person=self.person).count() > 1)
        self.assertEqual(current_student, student_bsn.find_by_user_and_discriminate(self.user))

    def test_no_offer_enrollment_valid(self):
        current_student = StudentFactory(person=self.person)
        OfferEnrollmentFactory(student=current_student,
                               enrollment_state=offer_enrollment_state.PENDING)
        OfferEnrollmentFactory(student=current_student, enrollment_state=None)
        self.assertTrue(Student.objects.filter(person=self.person).count() > 1)
        self.assertIsNone(student_bsn.find_by_user_and_discriminate(self.user))

    def test_cannot_discriminate(self):
        current_student = StudentFactory(person=self.person)
        current_academic_year = AcademicYearFactory(year=2020)
        current_education_group_year = EducationGroupYearFactory(academic_year=current_academic_year)
        OfferEnrollmentFactory(student=current_student, enrollment_state=offer_enrollment_state.SUBSCRIBED,
                               education_group_year=current_education_group_year)
        OfferEnrollmentFactory(student=self.student, enrollment_state=offer_enrollment_state.SUBSCRIBED,
                               education_group_year=current_education_group_year)
        self.assertTrue(Student.objects.filter(person=self.person).count() > 1)
        self.assertRaises(MultipleObjectsReturned, student_bsn.find_by_user_and_discriminate, self.user)

    def test_several_valid_enrollment_same_student(self):
        previous_student = StudentFactory(person=self.person)
        previous_academic_year = AcademicYearFactory(year=2019)
        previous_education_group = EducationGroupYearFactory(academic_year=previous_academic_year)
        current_academic_year = AcademicYearFactory(year=2020)
        current_education_group_year = EducationGroupYearFactory(academic_year=current_academic_year)
        OfferEnrollmentFactory(student=self.student, enrollment_state=offer_enrollment_state.SUBSCRIBED,
                               education_group_year=current_education_group_year)
        OfferEnrollmentFactory(student=self.student, enrollment_state=offer_enrollment_state.PROVISORY,
                               education_group_year=current_education_group_year)
        OfferEnrollmentFactory(student=previous_student, enrollment_state=offer_enrollment_state.PROVISORY,
                               education_group_year=previous_education_group)
        self.assertTrue(Student.objects.filter(person=self.person).count() > 1)
        self.assertTrue(OfferEnrollment.objects
                        .filter(student=self.student,
                                education_group_year__academic_year=current_academic_year).count() > 1)
        self.assertEqual(self.student, student_bsn.find_by_user_and_discriminate(self.user))
