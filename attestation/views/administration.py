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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
from typing import Dict

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse
from django.utils.functional import cached_property
from django.views.generic import TemplateView, FormView

from attestation.queues import student_attestation_status
from attestation.views.home import _make_registration_json_message, _make_attestation_data
from base.forms.base_forms import RegistrationIdForm
from base.models import student as student_mdl
from base.models.person import Person
from base.models.student import Student


class Administration(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    permission_required = 'base.is_faculty_administrator'
    template_name = 'admin/attestation_administration.html'


class AdministrationSelectStudent(Administration, FormView):
    form_class = RegistrationIdForm

    def form_valid(self, form):
        self.registration_id = form.cleaned_data['registration_id']
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('attestation_admin_view', args=[self.registration_id])


class AdministrationViewStudentAttestation(Administration, TemplateView):
    template_name = 'attestation_home_admin.html'

    @cached_property
    def student(self) -> Student:
        return student_mdl.find_by_registration_id(self.kwargs['registration_id'])

    @cached_property
    def person(self) -> Person:
        return self.request.user.person

    def get_attestations_data(self) -> Dict:
        json_message = _make_registration_json_message(self.student.registration_id)
        attestation_statuses_all_years_json_dict = student_attestation_status.fetch_json_attestation_statuses(
            json_message
        )
        return _make_attestation_data(attestation_statuses_all_years_json_dict, self.student, self.person)

    def get_context_data(self, **kwargs) -> Dict:
        return {
            **super().get_context_data(**kwargs),
            **self.get_attestations_data()
        }
