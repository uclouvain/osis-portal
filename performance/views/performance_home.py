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
import json
from typing import List, Dict, Optional

from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import MultipleObjectsReturned
from django.http import HttpRequest
from django.utils.functional import cached_property
from django.views.generic import TemplateView

import dashboard.views.home
from base.business import student as student_business
from base.models import student as student_model
from base.models.student import Student
from base.views import common
from performance import models as mdl_performance
from performance.models.enums import offer_registration_state
from performance.models.enums.offer_registration_state import OFFER_REGISTRATION_STATES
from performance.models.student_performance import StudentPerformance
from performance.views.main import _can_access_performance_administration

StudentPerformanceDict = Dict[str, str]


class PerformanceHomeMixin(LoginRequiredMixin, TemplateView):
    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            "student": self.student,
            "programs": self.student_programs if self.student else [],
            "registration_states_to_show": offer_registration_state.STATES_TO_SHOW_ON_PAGE
        }

    @cached_property
    def student_programs(self) -> List[StudentPerformanceDict]:
        query_result = mdl_performance.student_performance.search(registration_id=self.student.registration_id)
        list_student_programs = self.query_result_to_list(query_result)
        return list_student_programs

    def query_result_to_list(self, query_result: List[StudentPerformance]) -> List[StudentPerformanceDict]:
        performance_results_list = []
        for row in query_result:
            performance_dict = self.convert_student_performance_to_dict(row)
            allowed_registration_states = [value for key, value in OFFER_REGISTRATION_STATES]
            if performance_dict and performance_dict.get("offer_registration_state") in allowed_registration_states:
                performance_results_list.append(performance_dict)
        return performance_results_list

    @staticmethod
    def convert_student_performance_to_dict(
            student_performance_obj: StudentPerformance
    ) -> Optional[StudentPerformanceDict]:
        try:
            return {
                'academic_year': student_performance_obj.academic_year_template_formated,
                'acronym': student_performance_obj.acronym,
                'title': json.loads(
                    json.dumps(student_performance_obj.data)
                )["monAnnee"]["monOffre"]["offre"]["intituleComplet"],
                'pk': student_performance_obj.pk,
                'offer_registration_state': student_performance_obj.offer_registration_state
            }
        except Exception:
            return None

    def dispatch(self, request, *args, **kwargs):
        try:
            return super().dispatch(request, *args, **kwargs)
        except MultipleObjectsReturned:  # Exception raised by find_by_user_and_discriminate
            return dashboard.views.home.show_multiple_registration_id_error(self.request)


class PerformanceHomeAdmin(PerformanceHomeMixin, UserPassesTestMixin):
    template_name = "admin/performance_home_admin.html"

    def test_func(self):
        can_access_performance_administration = _can_access_performance_administration(self.request)
        has_student = self.student is not None
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
        return student_business.find_by_user_and_discriminate(self.request.user)


def _can_visualize_student_programs(request: HttpRequest, registration_id: str) -> bool:
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
    managed_programs = common.get_managed_programs(request.user)
    for stud_perfs in mdl_performance.student_performance.search(registration_id=registration_id):
        if stud_perfs.acronym in managed_programs:
            return True
    return False
