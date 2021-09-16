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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
from types import SimpleNamespace
from typing import List

from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import MultipleObjectsReturned
from django.utils.functional import cached_property
from django.views.generic import TemplateView
from osis_offer_enrollment_sdk.model.enrollment import Enrollment

from base.business import student as student_business
from base.models import student as student_model
from base.models.student import Student
from base.views import common
from dashboard.views import main as dash_main_view
from performance import models as mdl_performance
from performance.models.enums import offer_registration_state
from performance.models.student_performance import StudentPerformance
from performance.services.offer_enrollment import OfferEnrollmentService
from performance.views.main import _can_access_performance_administration


class PerformanceHomeMixin(LoginRequiredMixin, TemplateView):
    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            "student": self.student,
            "programs": self.offer_enrollments_list,
            "registration_states_to_show": offer_registration_state.STATES_TO_SHOW_ON_PAGE
        }

    @cached_property
    def offer_enrollments_list(self):
        offer_enrollments = OfferEnrollmentService.get_my_enrollments_list(self.student.person).results
        allowed_registration_states = [value for key, value in offer_registration_state.OFFER_REGISTRAION_STATES]
        offer_enrollments_to_display = []
        for offer_enrollment in offer_enrollments:
            student_performance = self._get_correspondant_student_performance(offer_enrollment)
            registration_state = student_performance and student_performance.offer_registration_state
            if registration_state in allowed_registration_states:
                offer_enrollments_to_display.append(
                    SimpleNamespace(
                        **offer_enrollment.to_dict(),
                        offer_registration_state=registration_state,
                        pk=student_performance.pk
                    )
                )
        return offer_enrollments_to_display

    def _get_correspondant_student_performance(self, offer_enrollment: Enrollment) -> StudentPerformance:
        return next(
            (student_performance
             for student_performance in self.student_performances
             if student_performance.acronym == offer_enrollment.acronym
             and student_performance.academic_year == offer_enrollment.year),
            None
        )

    @cached_property
    def student_performances(self) -> List[StudentPerformance]:
        if self.student:
            return StudentPerformance.objects.filter(
                registration_id=self.student.registration_id
            ).only('academic_year', "acronym", "offer_registration_state", "pk")
        return []


class PerformanceHomeAdmin(PerformanceHomeMixin, UserPassesTestMixin):
    template_name = "admin/performance_home_admin.html"

    def test_func(self):
        can_access_performance_administration = _can_access_performance_administration(self.request)
        has_student = self.student is not None
        print("TEST FUNC", can_access_performance_administration)
        print("OTHER FUNC",
              has_student and not _can_visualize_student_programs(self.request, self.student.registration_id))
        return can_access_performance_administration and not (
                has_student and not _can_visualize_student_programs(self.request, self.student.registration_id)
        )

    @cached_property
    def student(self) -> Student:
        return student_model.find_by_registration_id(self.kwargs['registration_id'])


class PerformanceHomeStudent(PerformanceHomeMixin, PermissionRequiredMixin):
    permission_required = "base.is_student"
    template_name = "performance_home_student.html"

    @cached_property
    def student(self) -> Student:
        try:
            print("YOLOOO", student_business.find_by_user_and_discriminate(self.request.user))
            return student_business.find_by_user_and_discriminate(self.request.user)
        except MultipleObjectsReturned:
            return dash_main_view.show_multiple_registration_id_error(self.request)


def _can_visualize_student_programs(request, registration_id):
    """
    Student cannot access administration
    User can visualize student programs if :
        - The user is faculty_administrator
        - The user is program manager of at least one of the program in the list of the student programs
    """
    if request.user.has_perm('base.is_faculty_administrator'):
        return True
    if request.user.has_perm('base.is_student'):
        return False
    managed_programs_as_dict = common.get_managed_program_as_dict(request.user)
    for stud_perfs in mdl_performance.student_performance.search(registration_id=registration_id):
        if stud_perfs.acronym in managed_programs_as_dict.get(stud_perfs.academic_year, []):
            return True
    return False
