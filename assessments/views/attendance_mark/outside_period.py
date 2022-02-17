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
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.shortcuts import redirect
from django.utils.functional import cached_property
from django.views.generic import TemplateView
from osis_assessments_sdk.model.attendance_mark_calendar import AttendanceMarkCalendar

from assessments.services.assessments import AttendanceMarkRemoteCalendar


class OutsidePeriod(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    permission_required = "base.is_student"

    name = 'outside-attendance-marks-period'

    # TemplateView
    template_name = "assessments/attendance_mark/outside_period.html"

    @cached_property
    def calendar(self) -> 'AttendanceMarkRemoteCalendar':
        return AttendanceMarkRemoteCalendar(self.request.user.person)

    def get_next_attendance_mark_period(self) -> 'AttendanceMarkCalendar':
        return self.calendar.get_next_academic_event()

    def get(self, request, *args, **kwargs):
        if self.calendar.get_opened_academic_events():
            return redirect('attendance-mark-select-offer')
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            "attendance_marks_request_start": self.get_next_attendance_mark_period().start_date.strftime('%d/%m/%Y'),
            "session_name": self.get_next_attendance_mark_period().month_session_name
        }
