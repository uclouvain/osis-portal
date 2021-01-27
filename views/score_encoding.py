############################################################################
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
############################################################################
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.translation import gettext as _
from osis_internship_sdk import ScoreGet
from osis_internship_sdk.rest import ApiException

from base.views import layout
from internship.models.period import Period
from internship.templatetags.selection_tags import only_number
from internship.views.api_client import InternshipAPIClient, get_paginated_results, get_first_paginated_result

APD_NUMBER = 15
COMMENTS_FIELDS = ['intermediary_evaluation', 'good_perf_ex', 'impr_areas', 'suggestions']


@login_required(login_url="/internship/auth/login/")
def view_score_encoding(request):
    master = _get_master_by_email(request.user.username)
    if master:
        allocations = _get_master_allocations(master['uuid'])
        for allocation in allocations:
            students_affectations = _get_students_affectations(
                specialty_uuid=allocation['specialty']['uuid'],
                organization_uuid=allocation['organization']['uuid'],
            )
            encoded_affectations = _get_students_affectations(
                specialty_uuid=allocation['specialty']['uuid'],
                organization_uuid=allocation['organization']['uuid'],
                with_score=True
            )
            amount_encoded = len(encoded_affectations)
            total_amount = len(students_affectations)
    else:
        messages.error(request, _('Access to internship is only authorized to students and internship masters'))
        return redirect(reverse('internship'))
    return layout.render(request, "internship_score_encoding.html", locals())


@login_required(login_url="/internship/auth/login/")
def view_score_encoding_sheet(request, specialty_uuid, organization_uuid):
    if request.GET.get('period'):
        selected_period = request.GET.get('period', "")
    else:
        active_period = _get_active_period()
        selected_period = active_period['name'] if active_period else ""

    apds = ['apd_{}'.format(index) for index in range(1, APD_NUMBER + 1)]

    specialty = _get_specialty(specialty_uuid)
    organization = _get_organization(organization_uuid)

    selected_period = selected_period if selected_period != "all" else ""
    students_affectations = _get_students_affectations(specialty_uuid, organization_uuid, selected_period)

    periods = Period.objects.filter(cohort__name=specialty.cohort.name).order_by('date_start')

    for affectation in students_affectations:
        affectation['score'] = _get_score(affectation['student']['uuid'], affectation['period']['uuid'])

    return layout.render(request, "internship_score_encoding_sheet.html", locals())


@login_required(login_url="/internship/auth/login/")
def view_score_encoding_form(request, specialty_uuid, organization_uuid, affectation_uuid):

    affectation = _get_affectation(affectation_uuid)
    period = affectation.period
    student = affectation.student

    score = _get_score(student.uuid, period.uuid)
    specialty = _get_specialty(specialty_uuid)
    organization = _get_organization(organization_uuid)

    apds = ['apd_{}'.format(index) for index in range(1, APD_NUMBER + 1)]

    if request.POST:
        comments = _build_comments(request.POST)
        objectives = _build_objectives(request.POST, apds)
        score = ScoreGet(
            student=score.student,
            period=score.period,
            cohort=score.cohort,
            comments=comments,
            objectives=objectives,
            **{key: request.POST.get(key) for key in ScoreGet.attribute_map.keys() if key in request.POST.keys()}
        )
        update = _update_score(student.uuid, period.uuid, score)
        if update:
            messages.add_message(
                request,
                messages.SUCCESS,
                _("Score updated successfully for {}'s internship during {}".format(
                    student.person.last_name, period.name
                ))
            )
        else:
            messages.add_message(request, messages.ERROR, _('An error occurred during score update'))
        return redirect(reverse('internship_score_encoding_form', kwargs={
            'specialty_uuid': specialty_uuid,
            'organization_uuid': organization_uuid,
            'affectation_uuid': affectation_uuid,
        }))

    available_grades = ['A', 'B', 'C', 'D', 'E']
    comments_fields = COMMENTS_FIELDS

    return layout.render(request, "internship_score_encoding_form.html", locals())


def _build_comments(post_data):
    return {field: post_data.get(field) for field in COMMENTS_FIELDS}


def _build_objectives(post_data, apds):
    apds_objectives = [post_data.get('obj-{}'.format(apd)) for apd in apds]
    return {'apds': [only_number(apd) for apd in apds_objectives if apd]}


def _get_master_by_email(email):
    return get_first_paginated_result(
        InternshipAPIClient().masters_get(search=email)
    )


def _get_master_allocations(master_uuid=None):
    return get_paginated_results(
        InternshipAPIClient().masters_uuid_allocations_get(uuid=master_uuid, current=True)
    )


def _get_specialty(specialty_uuid):
    return InternshipAPIClient().specialties_uuid_get(uuid=specialty_uuid)


def _get_organization(organization_uuid):
    return InternshipAPIClient().organizations_uuid_get(uuid=organization_uuid)


def _get_students_affectations(specialty_uuid, organization_uuid, period="", with_score=False):
    return get_paginated_results(
        InternshipAPIClient().students_affectations_specialty_organization_get(
            specialty=specialty_uuid,
            organization=organization_uuid,
            period=period,
            with_score=with_score
        )
    )


def _get_affectation(affectation_uuid):
    return InternshipAPIClient().students_affectations_uuid_get(uuid=affectation_uuid)


def _get_period(period_uuid):
    return InternshipAPIClient().periods_uuid_get(uuid=period_uuid)


def _get_active_period():
    return get_first_paginated_result(
        InternshipAPIClient().periods_get(active=True)
    )


def _get_score(student_uuid, period_uuid):
    try:
        return InternshipAPIClient().scores_student_uuid_period_uuid_get(
            student_uuid=student_uuid, period_uuid=period_uuid
        )
    except ApiException:
        return None


def _update_score(student_uuid, period_uuid, score):
    return InternshipAPIClient().scores_student_uuid_period_uuid_put(student_uuid, period_uuid, score_get=score)
