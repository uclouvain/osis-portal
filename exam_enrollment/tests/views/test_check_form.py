##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2022 Université catholique de Louvain (http://www.uclouvain.be)
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
from django.conf import settings
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from base.tests.factories.education_group_year import EducationGroupYearFactory
from base.tests.factories.offer_enrollment import OfferEnrollmentFactory
from base.tests.models import test_student, test_person, test_academic_year
from exam_enrollment.models.exam_enrollment_request import ExamEnrollmentRequest
from exam_enrollment.tests.factories.exam_enrollment_request import ExamEnrollmentRequestFactory
from exam_enrollment.tests.views.test_enrollment_form import HTTP_RESPONSE_NOTFOUND


class ExamEnrollmentFormTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='jsmith', email='jsmith@localhost', password='secret')
        cls.person = test_person.create_person_with_user(cls.user, first_name="James", last_name="Smith")
        cls.student = test_student.create_student_with_registration_person("12345678", cls.person)
        cls.current_academic_year = test_academic_year.create_academic_year_current()
        cls.off_enrol = OfferEnrollmentFactory(
            student=cls.student,
            education_group_year=EducationGroupYearFactory(academic_year=cls.current_academic_year)
        )

    def setUp(self) -> None:
        self.client.force_login(self.user)

        # Mock the OSIS Remote API Call
        self.offer_enrollment_row = SimpleNamespace(**{
            'acronym': self.off_enrol.education_group_year.acronym,
            'title': self.off_enrol.education_group_year.title,
            'year': self.off_enrol.education_group_year.academic_year.year,
        })

        self.offer_enrollment_patcher = mock.patch(
            "exam_enrollment.views.check_form.CheckForm.offer_enrollment",
            new_callable=mock.PropertyMock,
            return_value=self.offer_enrollment_row
        )
        self.mocked_offer_enrollment = self.offer_enrollment_patcher.start()
        self.addCleanup(self.offer_enrollment_patcher.stop)

    def test_check_exam_enrollment_form_up_to_date_in_db_with_document(self):
        educ_group_year = self.off_enrol.education_group_year
        ExamEnrollmentRequestFactory(
            student=self.student,
            offer_year_acronym=educ_group_year.acronym,
            document={"id": 1}
        )

        request_url = reverse(
            'check_exam_enrollment_form',
            args=[educ_group_year.acronym, educ_group_year.academic_year.year]
        )
        response = self.client.get(request_url)
        self.assertEqual(response.status_code, HttpResponse.status_code)

    def test_check_exam_enrollment_form_not_in_db(self):
        educ_group_year = self.off_enrol.education_group_year

        request_url = reverse(
            'check_exam_enrollment_form',
            args=[educ_group_year.acronym, educ_group_year.academic_year.year]
        )
        response = self.client.get(request_url)
        self.assertEqual(response.status_code, HTTP_RESPONSE_NOTFOUND)

    def test_check_exam_enrollment_form_up_to_date_in_db_with_empty_document(self):
        educ_group_year = self.off_enrol.education_group_year
        ExamEnrollmentRequestFactory(
            student=self.student,
            offer_year_acronym=educ_group_year.acronym,
            document={}
        )

        request_url = reverse(
            'check_exam_enrollment_form',
            args=[educ_group_year.acronym, educ_group_year.academic_year.year]
        )
        response = self.client.get(request_url)
        self.assertEqual(response.status_code, HTTP_RESPONSE_NOTFOUND)

    def test_check_exam_enrollment_form_outdated_in_db(self):
        request_timeout = settings.DEFAULT_QUEUE_TIMEOUT
        outdated_time = timezone.now() - timezone.timedelta(seconds=request_timeout + 1)
        educ_group_year = self.off_enrol.education_group_year
        ExamEnrollmentRequestFactory(
            student=self.student,
            offer_year_acronym=educ_group_year.acronym,
            document={"id": 1}
        )
        # We must update fetch_date without passing trough save() to bypass auto_now :
        exam_enroll_request_qs = ExamEnrollmentRequest.objects.filter(
            student=self.student,
            offer_year_acronym=educ_group_year.acronym
        )
        exam_enroll_request_qs.update(fetch_date=outdated_time)

        request_url = reverse(
            'check_exam_enrollment_form',
            args=[educ_group_year.acronym, educ_group_year.academic_year.year]
        )
        response = self.client.get(request_url)
        self.assertEqual(response.status_code, HTTP_RESPONSE_NOTFOUND)

    def test_check_exam_enrollment_form_not_in_db_without_offer_enrollment(self):
        educ_group_year = self.off_enrol.education_group_year
        self.off_enrol.delete()
        request_url = reverse(
            'check_exam_enrollment_form',
            args=[educ_group_year.acronym, educ_group_year.academic_year.year]
        )
        response = self.client.get(request_url)
        self.assertEqual(response.status_code, HTTP_RESPONSE_NOTFOUND)
