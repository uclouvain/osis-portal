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
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

PROFILE_TAB = "0"
DEMAND_TAB = "1"
PREREQUISITES_TAB = "2"
CURRICULUM_TAB = "3"
ACCOUNTING_TAB = "4"
SOCIOLOGICAL_SURVEY_TAB = "5"
ATTACHMENTS_TAB = "6"
SUBMISSION_TAB = "7"


def get_following_tab(request, active_tab, application):
    search_key = "following_" + active_tab + "_tab"
    next_tab = request.POST.get(search_key, None)
    application_id = None
    if application:
        application_id = application.id

    return get_redirection(next_tab, application_id)


def get_redirection(next_tab, application_id):
        reverse_name = None
        if next_tab == PROFILE_TAB:
            reverse_name = 'profile'
        if next_tab == DEMAND_TAB:
            reverse_name = 'applications'

        if next_tab == PREREQUISITES_TAB:
            reverse_name = 'diploma_update'

        if next_tab == CURRICULUM_TAB:
            reverse_name = 'curriculum_update'

        if next_tab == ACCOUNTING_TAB:
            reverse_name = 'accounting_update'

        if next_tab == SOCIOLOGICAL_SURVEY_TAB:
            reverse_name = 'sociological_survey'

        if next_tab == ATTACHMENTS_TAB:
            reverse_name = 'attachments'

        if next_tab == SUBMISSION_TAB:
            reverse_name = 'submission'

        if reverse_name:
            if application_id:
                return HttpResponseRedirect(reverse(reverse_name, args=(application_id,)))
            else:
                return HttpResponseRedirect(reverse(reverse_name), )

        return None
