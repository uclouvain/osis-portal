# -*- coding: utf-8 -*-
############################################################################
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
############################################################################
import requests
from django.conf import settings
from django.contrib.auth.decorators import login_required, permission_required

from base.views import layout
from internship import models as mdl_internship
from internship.decorators.cohort_view_decorators import redirect_if_not_in_cohort


@login_required
@permission_required('internship.can_access_internship', raise_exception=True)
@redirect_if_not_in_cohort
def view_place_evaluation(request, cohort_id):
    cohort = mdl_internship.cohort.Cohort.objects.get(pk=cohort_id)

    # TODO: get items through service using SDK

    items = requests.get(
        f"{settings.OSIS_INTERNSHIP_SDK_HOST}/place_evaluation_items/R6-2023/", headers={
            'Authorization': f'Token {settings.OSIS_PORTAL_TOKEN}'
        }
    ).json()['results']

    return layout.render(request, "place_evaluation.html", {'cohort': cohort, 'items': items})
