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
from itertools import groupby

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.views.generic import TemplateView


class Home(LoginRequiredMixin, TemplateView):
    template_name = "dashboard.html"

    def get_settings_url_context(self):
        return {
            'manage_courses_url': settings.OSIS_MANAGE_COURSES_URL,
            'osis_vpn_help_url': settings.OSIS_VPN_HELP_URL,
            'dissertation_url': settings.OSIS_DISSERTATION_URL,
            'score_encoding_url': settings.OSIS_SCORE_ENCODING_URL,
            'score_encoding_vpn_help_url': settings.OSIS_VPN_HELP_URL,
            'tiles': self.get_tiles_grouped_by_role(),
        }

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            **self.get_settings_url_context()
        }

    @staticmethod
    def get_tiles_data():
        tutor_tiles = [
            {
                'column': 'courses',
                'title': _('My applications'),
                'url': reverse('applications_overview'),
                'icon': 'far fa-id-card',
                'description': _('This process controls my applications.'),
                'role': 'TUTOR',
                'VPN': False,
                'app': 'attribution'
            },
            {
                'column': 'courses',
                'title': _('My teaching charge'),
                'url': reverse('attribution_home'),
                'icon': 'far fa-list-alt',
                'description': _('Read my teaching charge and access to lists and emails of students.'),
                'role': 'TUTOR',
                'VPN': False,
                'app': 'attribution'
            },
            {
                'column': 'courses',
                'title': _('Description fiche'),
                'url': settings.OSIS_MANAGE_COURSES_URL,
                'icon': 'far fa-file-alt',
                'description': _('Manage description fiche'),
                'role': 'TUTOR',
                'VPN': True,
                'app': 'attribution'
            },
            {
                'column': 'exams',
                'title': _('Lists of students enrolled to my exams'),
                'url': reverse('students_list'),
                'icon': 'fa fa-users',
                'description': _('Download lists of students enrolled to exams for online scores encoding (Excel).'),
                'role': 'TUTOR',
                'VPN': False,
                'app': 'attribution'
            },
            {
                'column': 'exams',
                'title': _('Scores encoding'),
                'url': settings.OSIS_SCORE_ENCODING_URL,
                'icon': 'far fa-hashtag',
                'description': _('Scores encoding of my students.'),
                'role': 'TUTOR',
                'VPN': True,
                'app': 'score_encoding'
            },
            {
                'column': 'submodules',
                'title': _('Dissertations'),
                'url': settings.OSIS_DISSERTATION_URL,
                'icon': 'far fa-edit',
                'description': _("Student's dissertations management."),
                'role': 'TUTOR',
                'VPN': True,
                'app': 'dissertation'
            },
            {
                'column': 'submodules',
                'title': _('Internships assessment'),
                'url': reverse('internship'),
                'icon': 'fa fa-user-md',
                'description': _("This process controls internships assessment."),
                'role': 'TUTOR',
                'VPN': False,
                'app': 'internship'
            },
        ]

        student_tiles = [
            {
                'column': 'personal',
                'title': _('My personal data'),
                'url': reverse('student_id_data_home'),
                'icon': 'far fa-id-card',
                'description': _('This process shows personal data.'),
                'role': 'STUDENT',
                'VPN': False,
                'app': 'base',
            },
            {
                'column': 'personal',
                'title': _('My attestations'),
                'url': reverse('attestation_home'),
                'icon': 'far fa-file-pdf',
                'description': _('This process controls my attestations.'),
                'role': 'STUDENT',
                'VPN': False,
                'app': 'attestation',
            },
            {
                'column': 'exams',
                'title': _('Annual program'),
                'url': reverse('performance_home'),
                'icon': 'fa fa-chart-line',
                'description': _('View my annual program and exam marks.'),
                'role': 'STUDENT',
                'VPN': False,
                'app': 'performance',
            },
            {
                'column': 'exams',
                'title': _('Exams enrollment'),
                'url': reverse('exam_enrollment_offer_choice'),
                'icon': 'fa fa-book',
                'description': _('Manage my exam registration.'),
                'role': 'STUDENT',
                'VPN': False,
                'app': 'exam_enrollment',
            },
            {
                'column': 'exams',
                'title': _('My attendance marks'),
                'url': reverse('attendance-mark-select-offer'),
                'icon': 'fa fa-user-slash',
                'description': _('Request an attendance mark (0/20).'),
                'role': 'STUDENT',
                'VPN': False,
                'app': 'assessments',
            },
            {
                'column': 'submodules',
                'title': _('Internships'),
                'url': reverse('internship'),
                'icon': 'fa fa-user-md',
                'description': _('This process controls students internships.'),
                'role': 'STUDENT',
                'VPN': False,
                'app': 'internship',
            }
        ]

        admission_tiles = [
            {
                'column': 'admission',
                'title': _('My enrolment request'),
                'url': reverse('admission:doctorate-list'),
                'icon': 'fa fa-address-card',
                'description': _("Create and manage my enrolment request for UCLouvain"),
                'role': 'ADMISSION',
                'VPN': False,
                'app': 'admission',
            },
            {
                'column': 'admission',
                'title': _('Manage doctorates'),
                'url': reverse('admission:supervised-list'),
                'icon': 'fa fa-address-card',
                'description': _("Access my doctoral students' requests."),
                'role': 'ADMISSION',
                'VPN': False,
                'app': 'admission',
            },
        ]

        return tutor_tiles + student_tiles

    def get_user_roles(self):
        roles = []
        if self.request.user.has_perm('base.is_tutor') or self.request.user.has_perm('base.is_master'):
            roles.append('TUTOR')
        if self.request.user.has_perm('base.is_student'):
            roles.append('STUDENT')
        roles.append('ADMISSION')
        return roles

    def get_tiles_grouped_by_role(self):
        tiles = [tile for tile in Home.get_tiles_data() if tile['role'] in self.get_user_roles()]
        tiles_by_role = {role: list(tiles) for role, tiles in groupby(tiles, key=lambda x: x['role'])}
        return tiles_by_role


def show_multiple_registration_id_error(request):
    msg = _("A problem was detected with your registration : 2 registration id's are linked to your user.</br> Please "
            "contact <a href=\"{registration_department_url}\" "
            "target=\"_blank\">the Registration department</a>. Thank you.") \
        .format(registration_department_url=settings.REGISTRATION_ADMINISTRATION_URL)
    messages.add_message(request, messages.ERROR, msg)
    return redirect(reverse('dashboard_home'))
