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
from django.utils.functional import cached_property
from django.views.generic import TemplateView
from osis_offer_enrollment_sdk.model.enrollment import Enrollment

from base.models import academic_year
from base.models.enums import offer_enrollment_state
from base.models.person import Person
from base.models.student import Student
from base.services.offer_enrollment import OfferEnrollmentService


class SelectionnerFormationView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    permission_required = "base.is_student"

    template_name = 'inscription_aux_cours/selectionner_formation.html'

    name = 'selectionner-formation'

    @cached_property
    def person(self) -> 'Person':
        return Person.objects.get(user=self.request.user)

    @cached_property
    def student(self) -> 'Student':
        if self.formations:
            registration_id = self.formations[0].student_registration_id
            return Student.objects.get(registration_id=registration_id)

    # TODO should be returned by api
    @cached_property
    def annee_academique(self) -> 'int':
        return academic_year.starting_academic_year().year

    @cached_property
    def formations(self) -> List['Enrollment']:
        return OfferEnrollmentService.get_my_enrollments_year_list(
            person=self.person,
            year=self.annee_academique,
            enrollment_state=[
                offer_enrollment_state.SUBSCRIBED,
                offer_enrollment_state.PROVISORY
            ]
        ) if self.person else []

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            'student': self.student,
            'formations': self.formations,
            'annee_academique': self.annee_academique,
        }
