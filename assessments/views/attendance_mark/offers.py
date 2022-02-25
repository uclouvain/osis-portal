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
from typing import List

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.shortcuts import redirect, get_object_or_404
from django.utils.functional import cached_property
from django.views.generic import TemplateView
from osis_offer_enrollment_sdk.model.enrollment_list import EnrollmentList

from assessments.business.attendance_mark import permission
from assessments.services import assessments as assessments_services
from base.models.student import Student
from base.services.offer_enrollment import OfferEnrollmentService


class SelectOffer(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    name = 'attendance-mark-select-offer'
    permission_required = "base.is_student"

    # TemplateView
    template_name = "assessments/attendance_mark/select_offer.html"

    @cached_property
    def student(self) -> 'Student':
        return get_object_or_404(
            Student.objects.select_related('person'),
            person__user=self.request.user
        )

    @cached_property
    def year(self):
        return assessments_services.AttendanceMarkRemoteCalendar(self.student.person).get_target_years_opened()[0]

    @cached_property
    def programs(self) -> List['EnrollmentList']:
        return OfferEnrollmentService.get_my_enrollments_year_list(self.student.person, self.year)

    def get(self, request, *args, **kwargs):
        if not permission.is_attendance_mark_period_opened(request.user):
            return redirect('outside-attendance-marks-period')
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            "student": self.student,
            "programs": self.programs
        }
