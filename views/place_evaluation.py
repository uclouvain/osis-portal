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

from django.contrib.auth.decorators import login_required, permission_required

from base.views import layout
from internship import models as mdl_internship
from internship.decorators.cohort_view_decorators import redirect_if_not_in_cohort
from internship.services.internship import InternshipAPIService


@login_required
@permission_required('internship.can_access_internship', raise_exception=True)
@redirect_if_not_in_cohort
def view_place_evaluations_list(request, cohort_id):
    cohort = mdl_internship.cohort.Cohort.objects.get(pk=cohort_id)
    affectations = InternshipAPIService.get_person_affectations(cohort=cohort, person=request.user.person)

    return layout.render(request, "place_evaluation_list.html", {'cohort': cohort, 'affectations': affectations})


@login_required
@permission_required('internship.can_access_internship', raise_exception=True)
@redirect_if_not_in_cohort
def view_place_evaluation_form(request, cohort_id, period_name):
    cohort = mdl_internship.cohort.Cohort.objects.get(pk=cohort_id)
    affectations = InternshipAPIService.get_person_affectations(cohort=cohort, person=request.user.person)

    evaluated_affectation = next(
        affectation for affectation in affectations if affectation['period']['name'] == period_name
    )

    items = InternshipAPIService.get_evaluation_items(cohort=cohort, person=request.user.person)

    return layout.render(request, "place_evaluation_form.html", {
        'cohort': cohort,
        'items': items,
        'affectation': evaluated_affectation
    })
