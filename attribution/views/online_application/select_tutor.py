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
import logging

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse
from django.views.generic import FormView

from base.forms.base_forms import GlobalIdForm

logger = logging.getLogger(settings.DEFAULT_LOGGER)


class SelectTutor(LoginRequiredMixin, PermissionRequiredMixin, FormView):
    template_name = "admin/applications_administration.html"
    permission_required = 'base.is_faculty_administrator'
    raise_exception = True
    http_method_names = ['get', 'post']
    form_class = GlobalIdForm

    def form_valid(self, form):
        self.registration_id = form.cleaned_data['registration_id']
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('visualize_tutor_applications', args=[self.registration_id])
