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
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.views.generic import TemplateView


class Home(LoginRequiredMixin, TemplateView):
    template_name = "dashboard.html"

    @staticmethod
    def get_settings_url_context():
        return {
            'manage_courses_url': settings.OSIS_MANAGE_COURSES_URL,
            'osis_vpn_help_url': settings.OSIS_VPN_HELP_URL,
            'dissertation_url': settings.OSIS_DISSERTATION_URL,
            'score_encoding_url': settings.OSIS_SCORE_ENCODING_URL,
            'score_encoding_vpn_help_url': settings.OSIS_VPN_HELP_URL
        }

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            **self.get_settings_url_context()
        }


def show_multiple_registration_id_error(request):
    msg = _("A problem was detected with your registration : 2 registration id's are linked to your user.</br> Please "
            "contact <a href=\"{registration_department_url}\" "
            "target=\"_blank\">the Registration department</a>. Thank you.") \
        .format(registration_department_url=settings.REGISTRATION_ADMINISTRATION_URL)
    messages.add_message(request, messages.ERROR, msg)
    return redirect(reverse('dashboard_home'))
