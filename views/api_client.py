# -*- coding: utf-8 -*-
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
from urllib.parse import urlparse

from osis_internship_sdk.api import internship_api
from osis_internship_sdk.api_client import ApiClient
from osis_internship_sdk.model.organization_get import OrganizationGet
from osis_internship_sdk.rest import ApiException

from frontoffice.settings.osis_sdk import internship as internship_sdk
from internship.models.enums.role_choice import ChoiceRole
from internship.models.score_encoding_utils import DEFAULT_PERIODS


class InternshipAPIClient:

    def __new__(cls):
        api_config = internship_sdk.build_configuration()
        return internship_api.InternshipApi(ApiClient(configuration=api_config))


# TODO: move each request to specific services

def get_first_paginated_result(response):
    return response.get('results')[0] if response.get('count') else None


def get_paginated_results(response):
    return response.get('results')


def get_master_by_email(email):
    return get_first_paginated_result(
        InternshipAPIClient().masters_get(search=email)
    )


def activate_master_account(master_uuid):
    return InternshipAPIClient().masters_uuid_activate_account_post(uuid=master_uuid)


def get_master_allocations(master_uuid=None):
    return get_paginated_results(
        InternshipAPIClient().masters_uuid_allocations_get(uuid=master_uuid, current=True)
    )


def get_mastered_allocations(specialty_uuid, organization_uuid):
    return get_paginated_results(
        InternshipAPIClient().masters_allocations_get(
            specialty=specialty_uuid, organization=organization_uuid, role=ChoiceRole.MASTER.value
        )
    )


def get_delegated_allocations(specialty_uuid, organization_uuid):
    return get_paginated_results(
        InternshipAPIClient().masters_allocations_get(
            specialty=specialty_uuid, organization=organization_uuid, role=ChoiceRole.DELEGATE.value
        )
    )


def get_specialty(specialty_uuid):
    return InternshipAPIClient().specialties_uuid_get(uuid=specialty_uuid)


def get_organization(organization_uuid) -> OrganizationGet:
    return InternshipAPIClient().organizations_uuid_get(uuid=organization_uuid)


def get_students_affectations_count(specialty_uuid, organization_uuid):
    return InternshipAPIClient().students_affectations_specialty_organization_stats_get(
        specialty=specialty_uuid, organization=organization_uuid
    )


def get_paginated_students_affectations(specialty_uuid, organization_uuid, period, **kwargs):
    response = get_students_affectations(specialty_uuid, organization_uuid, period, **kwargs)
    next = urlparse(response['next']).query if response['next'] else ''
    previous = urlparse(response['previous']).query if response['previous'] else ''
    results = get_paginated_results(response)
    count = response['count']
    return results, previous, next, count


def get_students_affectations(specialty_uuid, organization_uuid, period=DEFAULT_PERIODS, **kwargs):
    return InternshipAPIClient().students_affectations_specialty_organization_get(
        specialty=specialty_uuid,
        organization=organization_uuid,
        period=period,
        **kwargs
    )


def get_affectation(affectation_uuid):
    return InternshipAPIClient().students_affectations_uuid_get(uuid=affectation_uuid)


def get_period(period_uuid):
    return InternshipAPIClient().periods_uuid_get(uuid=period_uuid)


def get_active_period():
    return get_first_paginated_result(
        InternshipAPIClient().periods_get(active=True)
    )


def get_score(score_uuid):
    try:
        return InternshipAPIClient().scores_uuid_get(score_uuid)
    except ApiException:
        return None


def update_score(score):
    data, status, headers = InternshipAPIClient().scores_uuid_put(
        score.uuid,
        score_get=score,
        _return_http_data_only=False
    )
    return status == 200


def post_master(master):
    return InternshipAPIClient().masters_post(master_get=master)


def post_master_allocation(allocation):
    return InternshipAPIClient().masters_allocations_post(
        allocation_get=allocation,
    )


def delete_master_allocation(allocation_uuid):
    data, status, headers = InternshipAPIClient().masters_allocations_uuid_delete(
        uuid=allocation_uuid,
        _return_http_data_only=False
    )
    return status == 204


def validate_internship_score(affectation_uuid):
    try:
        return InternshipAPIClient().scores_affectation_uuid_validate_post(
            affectation_uuid=affectation_uuid,
            _return_http_data_only=False
        )
    except ApiException as e:
        return e.body, e.status, e.headers
