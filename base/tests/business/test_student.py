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
from types import SimpleNamespace

import mock
from django.contrib.auth.models import Group
from django.core.exceptions import MultipleObjectsReturned
from django.test import TestCase

from base.business import student as student_bsn
from base.models.student import Student
from base.services.offer_enrollment import OfferEnrollmentBusinessException
from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.person import PersonFactory
from base.tests.factories.student import StudentFactory
from base.tests.factories.user import UserFactory
from frontoffice.settings.osis_sdk.utils import MultipleApiBusinessException, ApiBusinessException


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
        self.current_academic_year = AcademicYearFactory(current=True)
        self.client.force_login(self.person.user)

        self.offer_enrollment = SimpleNamespace(
            results=SimpleNamespace(**{
                'acronym': "DROI1BA",
                'title': "TITLE",
                'year': self.current_academic_year.year,
                'student_registration_id': self.student.registration_id
            }),
            count=1
        )

        self.student_enrolls_patcher = mock.patch(
            "base.services.offer_enrollment.OfferEnrollmentService.get_enrollments_list",
            return_value=self.offer_enrollment
        )
        self.mocked_enrolls_list = self.student_enrolls_patcher.start()
        self.addCleanup(self.student_enrolls_patcher.stop)

    def test_one_student(self):
        self.assertEqual(self.student, student_bsn.find_by_user_and_discriminate(self.user))

    def test_no_student(self):
        another_user = UserFactory()
        PersonFactory(user=another_user)
        self.assertIsNone(student_bsn.find_by_user_and_discriminate(another_user))

    def test_no_offer_enrollment_valid(self):
        StudentFactory(person=self.person)
        self.mocked_enrolls_list.return_value = SimpleNamespace(
            results=[],
            count=0
        )
        self.assertTrue(Student.objects.filter(person=self.person).count() > 1)
        self.assertIsNone(student_bsn.find_by_user_and_discriminate(self.user))

    def test_cannot_discriminate(self):
        StudentFactory(person=self.person)
        self.mocked_enrolls_list.side_effect = MultipleApiBusinessException(
            exceptions={
                ApiBusinessException(status_code=OfferEnrollmentBusinessException.DoubleNOMA.value, detail=''), }
        )
        self.assertRaises(MultipleObjectsReturned, student_bsn.find_by_user_and_discriminate, self.user)
