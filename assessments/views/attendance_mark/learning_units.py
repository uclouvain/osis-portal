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
from typing import Optional, List

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils.functional import cached_property
from django.views.generic import TemplateView
from osis_assessments_sdk.model.attendance_mark_calendar import AttendanceMarkCalendar
from osis_assessments_sdk.model.attendance_mark_requested import AttendanceMarkRequested
from osis_exam_enrollment_sdk.model.exam_enrollment import ExamEnrollment
from osis_offer_enrollment_sdk.model.enrollment import Enrollment

from assessments.services import assessments as assessments_service
from base.models.student import Student
from base.services.offer_enrollment import OfferEnrollmentService
from exam_enrollment.services import exam_enrollment as exam_enrollment_service


class ListExamEnrollments(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    name = 'attendance-mark-list-exam-enrollments'
    permission_required = "base.is_student"

    # TemplateView
    template_name = "assessments/attendance_mark/list_exam_enrollments.html"

    @property
    def program_acronym(self) -> str:
        return self.kwargs['program_acronym']

    @property
    def year(self) -> int:
        return self.current_attendance_mark_event.authorized_target_year

    @property
    def session_number(self) -> int:
        return self.current_attendance_mark_event.session_number

    @cached_property
    def student(self) -> 'Student':
        return get_object_or_404(Student.objects.select_related('person'), person__user=self.request.user)

    @cached_property
    def offer_enrollments(self) -> List['Enrollment']:
        return OfferEnrollmentService.get_my_enrollments_year_list(self.student.person, self.year)

    @cached_property
    def program_title(self) -> str:
        return next(
            (program.title for program in self.offer_enrollments if program.acronym == self.program_acronym),
            ""
        )

    @cached_property
    def current_attendance_mark_event(self) -> Optional['AttendanceMarkCalendar']:
        return next(
            iter(assessments_service.AttendanceMarkRemoteCalendar(self.student.person).get_opened_academic_events()),
            None
        )

    @cached_property
    def exam_enrollments(self) -> List['ExamEnrollment']:
        return exam_enrollment_service.ExamEnrollmentService.get_enrollments(
            program_acronym=self.program_acronym,
            year=self.year,
            session=self.session_number,
            person=self.student.person
        )

    @cached_property
    def requested_attendance_marks(self) -> List['AttendanceMarkRequested']:
        return assessments_service.AttendanceMarkService.get_requested_attendance_marks(self.student.person)

    def get(self, request, *args, **kwargs):
        if not self.current_attendance_mark_event:
            return redirect('outside-attendance-marks-period')
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        requested_attendance_marks_by_code = {
            requested_attendance_mark['code']: requested_attendance_mark
            for requested_attendance_mark in self.requested_attendance_marks
        }
        return {
            **super().get_context_data(**kwargs),
            "student": self.student,
            "program_title": self.program_title,
            "program_acronym": self.program_acronym,
            "session": self.current_attendance_mark_event.month_session_name,
            "year": self.year,
            "scoresheet_url": reverse("performance_home"),
            "exam_enrollments": self.exam_enrollments,
            "requested_attendance_marks_by_code": requested_attendance_marks_by_code
        }
