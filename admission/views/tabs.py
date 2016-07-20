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
from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils import translation
from django.utils.translation import ugettext_lazy as _
from admission import models as mdl
from admission.views import demande_validation


def init(request):
    print('init')

    tabs = {"tab_profile": True,
            "tab_applications": True,
            "tab_diploma": True,
            "tab_curriculum": True,
            "tab_accounting": True,
            "tab_sociological": True,
            "tab_attachments": True,
            "tab_submission": True}
    #
    # applicant = mdl.applicant.find_by_user(request.user)
    # if not demande_validation.validate_profil(applicant):
    #     tabs['tab_applications'] = False
    #     tabs['tab_diploma'] = False
    #     tabs['tab_curriculum'] = False
    #     tabs['tab_accounting'] = False
    #     tabs['tab_sociological'] = False
    #     tabs['tab_attachments'] = False
    #     tabs['tab_submission'] = False
    return tabs


def get_tabs_status(request):
    print('get_tabs_status')
    tabs = {"tab_profile": True,
            "tab_applications": True,
            "tab_diploma": False,
            "tab_curriculum": False,
            "tab_accounting": False,
            "tab_sociological": False,
            "tab_attachments": False,
            "tab_submission": False}
    applicant = mdl.applicant.find_by_user(request.user)
    if not demande_validation.validate_profil(applicant):
        tabs['tab_applications'] = False


    return tabs
