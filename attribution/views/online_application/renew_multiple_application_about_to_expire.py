##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2023 Université catholique de Louvain (http://www.uclouvain.be)
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
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.utils.translation import gettext_lazy as _
from django.views import View

from attribution.services.application import ApplicationService
from attribution.utils import permission

logger = logging.getLogger(settings.DEFAULT_LOGGER)


class RenewMultipleAttributionsAboutToExpireView(LoginRequiredMixin, View):

    def post(self, request, *args, **kwargs):
        if not permission.is_online_application_opened(self.request.user):
            return redirect("outside_applications_period")

        post_data = dict(request.POST.lists())
        vacant_course_codes = [param.split("_")[-1] for param in post_data if "vacant_course_" in param]

        if vacant_course_codes:
            ApplicationService.renew_attributions_about_to_expire(vacant_course_codes, self.request.user.person)
        else:
            messages.add_message(request, messages.ERROR, _('No attribution renewed'))
        return redirect('applications_overview')
