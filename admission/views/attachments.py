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
from django.shortcuts import render
from admission import models as mdl
from admission.views import demande_validation
from admission.views import tabs


def update(request, application_id=None):
    first = True
    if application_id:
        application = mdl.application.find_by_id(application_id)
        first = False
    else:
        application = mdl.application.init_application(request.user)
    applicant = mdl.applicant.find_by_user(request.user)
    tab_status = tabs.init(request)
    return render(request, "home.html", {'tab_active': 6,
                                         "first": first,
                                         "application": application,                                         
                                         "validated_profil": demande_validation.validate_profil(applicant),
                                         "validated_diploma": demande_validation.validate_diploma(application),
                                         "validated_curriculum": demande_validation.validate_curriculum(application),
                                         "validated_application": demande_validation.validate_application(application),
                                         "validated_accounting": demande_validation.validate_accounting(),
                                         "validated_sociological": demande_validation.validate_sociological(),
                                         "validated_attachments": demande_validation.validate_attachments(),
                                         "validated_submission": demande_validation.validate_submission(),
                                         'tab_profile': tab_status['tab_profile'],
                                         'tab_applications': tab_status['tab_applications'],
                                         'tab_diploma': tab_status['tab_diploma'],
                                         'tab_curriculum': tab_status['tab_curriculum'],
                                         'tab_accounting': tab_status['tab_accounting'],
                                         'tab_sociological': tab_status['tab_sociological'],
                                         'tab_attachments': tab_status['tab_attachments'],
                                         'tab_submission': tab_status['tab_submission']})
