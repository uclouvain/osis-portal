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
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from django.urls import reverse
from django.views.generic import FormView

from base.forms.base_forms import GlobalIdForm

logger = logging.getLogger(settings.DEFAULT_LOGGER)


class SelectTutorForAttribution(LoginRequiredMixin, PermissionRequiredMixin, FormView):
    template_name = "admin/attribution_administration.html"
    permission_required = 'base.is_faculty_administrator'
    raise_exception = True
    form_class = GlobalIdForm

    def form_valid(self, form):
        self.global_id = form.cleaned_data['global_id']
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('tutor_charge_admin', kwargs={'global_id': self.global_id})
