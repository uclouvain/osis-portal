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
from typing import Optional

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from django.views.generic import FormView
from osis_assessments_sdk.model.attendance_mark_calendar import AttendanceMarkCalendar

from assessments.business.attendance_mark import permission
from assessments.forms.attendance_mark.request_attendance_mark_form import RequestAttendanceMarkForm
from assessments.services import assessments as assessments_services
from base.models.person import Person
from base.views.mixin import AjaxTemplateMixin
from inscription_evaluation.services import exam_enrollment as exam_enrollment_service


class RequestAttendanceMarkFormView(AjaxTemplateMixin, LoginRequiredMixin, PermissionRequiredMixin, FormView):
    name = 'request-attendance-mark'
    permission_required = "base.is_student"

    # FormView
    template_name = "assessments/attendance_mark/request_attendance_mark_inner.html"

    form_class = RequestAttendanceMarkForm

    def dispatch(self, request, *args, **kwargs):
        if not permission.is_attendance_mark_period_opened(request.user):
            return redirect('outside-attendance-marks-period')
        return super().dispatch(request, *args, **kwargs)

    @property
    def person(self) -> 'Person':
        return self.request.user.person

    @cached_property
    def current_attendance_mark_event(self) -> Optional['AttendanceMarkCalendar']:
        return assessments_services.AttendanceMarkRemoteCalendar(self.person).get_opened_academic_events()[0]

    @cached_property
    def year(self):
        return self.current_attendance_mark_event.authorized_target_year

    @cached_property
    def session_number(self):
        return self.current_attendance_mark_event.session_number

    @cached_property
    def learning_unit_code(self) -> str:
        return self.kwargs['learning_unit_code']

    @cached_property
    def program_acronym(self) -> str:
        return self.kwargs['program_acronym']

    @cached_property
    def learning_unit_title(self) -> str:
        enrollments = exam_enrollment_service.ExamEnrollmentService.get_enrollments(
            program_acronym=self.program_acronym,
            year=self.year,
            session=self.session_number,
            person=self.person
        )
        return next(
            (
                enrollment.learning_unit_title
                for enrollment in enrollments
                if enrollment.learning_unit_code == self.learning_unit_code
            ),
            ''
        )

    def form_valid(self, form):
        response = assessments_services.AttendanceMarkService.request_attendance_mark(
            learning_unit_code=self.learning_unit_code,
            person=self.person
        )
        if not response:
            error_message = _('Unexpected error')
            messages.add_message(self.request, messages.ERROR, error_message, "alert-danger")
        else:
            success_message = _(
                'The attendance mark request has been received. '
                'A confirmation email is sent to %(email)s.'
            ) % {'email': self.person.email}
            messages.add_message(self.request, messages.SUCCESS, success_message)

        return super().form_valid(form)

    def get_success_url(self):
        return reverse("attendance-mark-list-exam-enrollments", kwargs={"program_acronym": self.program_acronym})

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            'form': self.get_form(self.form_class),
            'learning_unit_title': self.learning_unit_title
        }
