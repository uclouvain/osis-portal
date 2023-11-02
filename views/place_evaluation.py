# -*- coding: utf-8 -*-
############################################################################
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
############################################################################
import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from osis_internship_sdk.exceptions import ForbiddenException

from base.views import layout
from internship.decorators.cohort_view_decorators import redirect_if_not_in_cohort
from internship.services.internship import InternshipAPIService
from internship.templatetags.period import str_to_iso_date


@login_required
@permission_required('base.can_access_internship', raise_exception=True)
@redirect_if_not_in_cohort
def view_place_evaluations_list(request, cohort_id):
    cohort = InternshipAPIService.get_cohort_detail(cohort_name=cohort_id, person=request.user.person)
    affectations = InternshipAPIService.get_person_affectations(cohort=cohort, person=request.user.person)
    publication_allowed = str_to_iso_date(cohort.publication_start_date) <= datetime.date.today()
    return layout.render(request, "place_evaluation_list.html", {
        'cohort': cohort,
        'affectations': affectations,
        'publication_allowed': publication_allowed
    })


@login_required
@permission_required('base.can_access_internship', raise_exception=True)
@redirect_if_not_in_cohort
def view_place_evaluation_form(request, cohort_id, period_name):
    cohort = InternshipAPIService.get_cohort_detail(cohort_name=cohort_id, person=request.user.person)
    affectations = InternshipAPIService.get_person_affectations(cohort=cohort, person=request.user.person)
    evaluated_affectation = next(
        affectation for affectation in affectations if affectation['period']['name'] == period_name
    )

    evaluation = InternshipAPIService.get_evaluation(person=request.user.person, affectation=evaluated_affectation)
    items = InternshipAPIService.get_evaluation_items(cohort=cohort, person=request.user.person)

    if request.POST:
        try:
            InternshipAPIService.update_evaluation(
                person=request.user.person,
                affectation=evaluated_affectation,
                evaluation={
                    item.uuid: {
                        "statement": item.statement,
                        "response": request.POST.get(item.uuid)
                    } for item in items
                }
            )
            messages.add_message(
                request=request,
                level=messages.SUCCESS,
                message=_("Successfully updated place evaluation for {} - {} - {}").format(
                    evaluated_affectation.period.name,
                    evaluated_affectation.speciality.name,
                    evaluated_affectation.organization.name,
                )
            )
        except ForbiddenException:
            messages.add_message(request, messages.ERROR, _("Permission denied for this action"))
        return redirect(reverse('place_evaluation_list', kwargs={'cohort_id': cohort_id}))

    return layout.render(request, "place_evaluation_form.html", {
        'cohort': cohort,
        'items': items,
        'affectation': evaluated_affectation,
        'evaluation': evaluation,
    })
