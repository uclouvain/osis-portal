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
from django.utils import translation
from django.utils.translation import ugettext_lazy as _
from admission import models as mdl
from admission.views import demande_validation

# Not really useful for the moment, but I think it could be useful when we will work on the enabled/disabled tab for
# the admission.  LV


def init(request):
    tabs = {"tab_profile": True,
            "tab_applications": True,
            "tab_diploma": True,
            "tab_curriculum": True,
            "tab_accounting": True,
            "tab_sociological": True,
            "tab_attachments": True,
            "tab_submission": True}

    return tabs


def get_tabs_status(request):

    tabs = {"tab_profile": True,
            "tab_applications": True,
            "tab_diploma": False,
            "tab_curriculum": False,
            "tab_accounting": False,
            "tab_sociological": False,
            "tab_attachments": False,
            "tab_submission": False}
    applicant = mdl.applicant.find_by_user(request.user)
    if not demande_validation.validate_profil(applicant, request.user):
        tabs['tab_applications'] = False

    return tabs
