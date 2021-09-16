##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2021 Université catholique de Louvain (http://www.uclouvain.be)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
from typing import List

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.exceptions import MultipleObjectsReturned
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView
from osis_offer_enrollment_sdk.model.enrollment import Enrollment

from base.business import student as student_business
from base.models import academic_year
from base.models.academic_year import AcademicYear
from dashboard.views import main as dash_main_view
from exam_enrollment.services.offer_enrollment import OfferEnrollmentService


class OfferChoice(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    permission_required = "base.is_student"
    template_name = 'offer_choice.html'

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            'programs': self.offer_enrollments_list,
            'student': self.student
        }

    @cached_property
    def student(self):
        try:
            return student_business.find_by_user_and_discriminate(self.request.user)
        except MultipleObjectsReturned:
            return dash_main_view.show_multiple_registration_id_error(self.request)

    def get(self, *args, **kwargs):
        if not self.offer_enrollments_list:
            messages.add_message(
                self.request,
                messages.WARNING,
                _('no_offer_enrollment_found').format(self.current_academic_year)
            )
            return redirect(reverse('dashboard_home'))
        return super().get(*args, **kwargs)

    @cached_property
    def offer_enrollments_list(self) -> List[Enrollment]:
        return OfferEnrollmentService.get_my_enrollments_year_list(
            person=self.student.person,
            year=self.current_academic_year.year
        ).results

    @cached_property
    def current_academic_year(self) -> AcademicYear:
        return academic_year.starting_academic_year()
