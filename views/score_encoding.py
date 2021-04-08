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
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.translation import gettext as _
from osis_internship_sdk.models import ScoreGet

from base.views import layout
from internship.decorators.score_encoding_view_decorators import redirect_if_not_master
from internship.models.period import Period
from internship.models.score_encoding_utils import DEFAULT_PERIODS, APDS, COMMENTS_FIELDS, MIN_APDS, MAX_APDS, \
    AVAILABLE_GRADES
from internship.services.internship import InternshipAPIService
from internship.templatetags.selection_tags import only_number


@login_required
@redirect_if_not_master
def view_score_encoding(request):
    master = InternshipAPIService.get_master_by_email(request.user.email)
    allocations = InternshipAPIService.get_master_allocations(master['uuid'])
    for allocation in allocations:
        stats = InternshipAPIService.get_students_affectations_count(
            specialty_uuid=allocation['specialty']['uuid'],
            organization_uuid=allocation['organization']['uuid'],
        )
        allocation.__dict__['total_amount'] = stats['total_count']
        allocation.__dict__['amount_encoded'] = stats['validated_count']
    return layout.render(request, "internship_score_encoding.html", locals())


@login_required
@redirect_if_not_master
def view_score_encoding_sheet(request, specialty_uuid, organization_uuid):
    if request.GET.get('period'):
        selected_period = request.GET.get('period', "")
    else:
        active_period = InternshipAPIService.get_active_period()
        selected_period = active_period['name'] if active_period else DEFAULT_PERIODS

    pagination_params = {'limit': int(request.GET.get('limit', '0')), 'offset': int(request.GET.get('offset', '0'))}

    apds = APDS

    specialty = InternshipAPIService.get_specialty(specialty_uuid)
    organization = InternshipAPIService.get_organization(organization_uuid)

    students_affectations, previous, next, count = InternshipAPIService.get_paginated_students_affectations(
        specialty_uuid, organization_uuid, selected_period, **pagination_params
    )

    periods = Period.objects.filter(cohort__uuid=specialty.cohort.uuid).order_by('date_start')

    return layout.render(request, "internship_score_encoding_sheet.html", locals())


@login_required
@redirect_if_not_master
def view_score_encoding_form(request, specialty_uuid, organization_uuid, affectation_uuid):

    affectation = InternshipAPIService.get_affectation(affectation_uuid)
    period = affectation.period
    student = affectation.student

    score = InternshipAPIService.get_score(affectation_uuid)
    specialty = InternshipAPIService.get_specialty(specialty_uuid)
    organization = InternshipAPIService.get_organization(organization_uuid)

    apds = APDS
    comments_fields = COMMENTS_FIELDS
    available_grades = AVAILABLE_GRADES

    if request.POST:
        score = _build_score_to_update(request.POST, score)
        if not _validate_score(request.POST):
            _show_invalid_update_msg(request)
            return layout.render(request, "internship_score_encoding_form.html", locals())
        if InternshipAPIService.update_score(affectation_uuid, score):
            _show_success_update_msg(request, period, student)
            return redirect(reverse('internship_score_encoding_sheet', kwargs={
                'specialty_uuid': specialty_uuid,
                'organization_uuid': organization_uuid,
            }) + '?period={}'.format(period.name))
        messages.add_message(request, messages.ERROR, _('An error occurred during score update'))

    return layout.render(request, "internship_score_encoding_form.html", locals())


@login_required
@redirect_if_not_master
def score_encoding_validate(request, affectation_uuid):
    data, status, headers = InternshipAPIService.validate_internship_score(affectation_uuid)
    is_success = status == 204
    return JsonResponse({} if is_success else {'error': _('An error occured during validation')})


def _show_success_update_msg(request, period, student):
    messages.add_message(
        request,
        messages.SUCCESS,
        _("Score updated successfully for {}'s internship during {}".format(
            student.last_name, period.name
        ))
    )


def _show_invalid_update_msg(request):
    messages.add_message(
        request,
        messages.ERROR,
        _("You must evaluate minimum {} and maximum {} APDs").format(MIN_APDS, MAX_APDS)
    )


def _build_score_to_update(post_data, score):
    comments = _build_comments(post_data)
    objectives = _build_objectives(post_data)
    score = ScoreGet(
        uuid=score.uuid,
        comments=comments,
        objectives=objectives,
        **{key: post_data.get(key) for key in ScoreGet.attribute_map.keys() if key in post_data.keys()}
    )
    return score


def _build_comments(post_data):
    return {field_id: post_data.get(field_id) for field_id, field_label in COMMENTS_FIELDS}


def _build_objectives(post_data):
    apds_objectives = [post_data.get('obj-{}'.format(apd)) for apd in APDS]
    return {'apds': [only_number(apd) for apd in apds_objectives if apd]}


def _validate_score(post_data):
    apds_data = [post_data.get(apd) for apd in APDS if post_data.get(apd)]
    return MIN_APDS <= len(apds_data) <= MAX_APDS
