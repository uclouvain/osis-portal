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
from django.test import TestCase

import mock
from django.http import HttpResponseForbidden, HttpResponse
from django.urls import reverse

from assessments.tests.factories.services.assessments import InMemoryAttendanceMarkRemoteCalendar, \
    AttendanceMarkSession1CalendarFactory
from base.tests.factories.person import PersonFactory
from base.tests.factories.student import StudentFactory


class TestListExamEnrollments(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.student = StudentFactory()
        cls.url = reverse("attendance-mark-list-exam-enrollments", args=['SINF1BA'])

    def setUp(self):
        self.client.force_login(self.student.person.user)

        self.remote_calendar = InMemoryAttendanceMarkRemoteCalendar(self.student.person)

        self.get_enrollments_list_patcher = mock.patch(
            "base.services.offer_enrollment.OfferEnrollmentService.get_my_enrollments_year_list"
        )
        self.mocked_get_enrollments_list = self.get_enrollments_list_patcher.start()
        self.mocked_get_enrollments_list.return_value = []
        self.addCleanup(self.get_enrollments_list_patcher.stop)

        self.attendance_mark_remote_calendar_patcher = mock.patch(
            "assessments.services.assessments.AttendanceMarkRemoteCalendar",
        )
        self.mocked_attendance_mark_remote_calendar = self.attendance_mark_remote_calendar_patcher.start()
        self.mocked_attendance_mark_remote_calendar.return_value = self.remote_calendar
        self.addCleanup(self.attendance_mark_remote_calendar_patcher.stop)

        self.education_group_service_patcher = mock.patch(
            "education_group.services.education_group.EducationGroupService",
        )
        self.mocked_education_group_service = self.education_group_service_patcher.start()
        self.addCleanup(self.education_group_service_patcher.stop)

        self.exam_enrollment_service_patcher = mock.patch(
            'exam_enrollment.services.exam_enrollment.ExamEnrollmentService'
        )
        self.mocked_exam_enrollment_service = self.exam_enrollment_service_patcher.start()
        self.addCleanup(self.exam_enrollment_service_patcher.stop)

        self.attendance_mark_service_patcher = mock.patch(
            'assessments.services.assessments.AttendanceMarkService'
        )
        self.mocked_attendance_mark_service = self.attendance_mark_service_patcher.start()
        self.addCleanup(self.attendance_mark_service_patcher.stop)

    def test_non_student_should_have_permission_denied(self):
        non_student = PersonFactory()
        self.client.force_login(non_student.user)

        response = self.client.get(self.url)
        self.assertEqual(
            response.status_code,
            HttpResponseForbidden.status_code
        )

    def test_should_be_redirected_to_outside_period_page_when_outside_of_attendance_mark_period(self):
        response = self.client.get(self.url)

        self.assertRedirects(
            response,
            reverse('outside-attendance-marks-period'),
            fetch_redirect_response=False
        )

    def test_student_should_access_page_when_during_attendance_mark_period(self):
        self.remote_calendar._calendars.append(
            AttendanceMarkSession1CalendarFactory(is_open=True)
        )
        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            HttpResponse.status_code
        )
        self.assertTemplateUsed(
            response,
            "assessments/attendance_mark/list_exam_enrollments.html"
        )
