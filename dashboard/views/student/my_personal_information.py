##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2016 Université catholique de Louvain (http://www.uclouvain.be)
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
import logging

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.exceptions import MultipleObjectsReturned
from django.utils.functional import cached_property
from django.views.generic import TemplateView, FormView

import dashboard.views.home
from base.business import student as student_business
from base.forms.base_forms import RegistrationIdForm
from base.models.student import Student
from base.views import layout
from dashboard.business import id_data as id_data_bus

logger = logging.getLogger(settings.DEFAULT_LOGGER)


class MyPersonalInformation(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    permission_required = 'base.is_student'
    template_name = "student/id_data_home.html"
    raise_exception = True

    @cached_property
    def student(self) -> Student:
        return student_business.find_by_user_and_discriminate(self.request.user)

    def dispatch(self, request, *args, **kwargs):
        try:
            return super().dispatch(request, *args, **kwargs)
        except MultipleObjectsReturned:  # Exception raised by find_by_user_and_discriminate
            logger.exception('User {} returned multiple students.'.format(request.user.username))
            return dashboard.views.home.show_multiple_registration_id_error(self.request)

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            'data': id_data_bus.get_student_id_data(registration_id=self.student.registration_id)
        }


class MyPersonalInformationAdmin(LoginRequiredMixin, PermissionRequiredMixin, FormView):
    template_name = "admin/student_id_data_administration.html"
    permission_required = 'base.is_faculty_administrator'
    raise_exception = True
    form_class = RegistrationIdForm

    def form_valid(self, form):
        registration_id = form.cleaned_data['registration_id']
        data = id_data_bus.get_student_id_data(registration_id=registration_id)
        return layout.render(self.request, "admin/student_id_data.html", data)
