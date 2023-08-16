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
import json
from urllib.parse import urlparse

from osis_internship_sdk import ApiException, ApiClient
from osis_internship_sdk.api import internship_api
from osis_internship_sdk.model.organization_get import OrganizationGet
from osis_internship_sdk.model.place_evaluation_get import PlaceEvaluationGet

from frontoffice.settings.osis_sdk import internship as internship_sdk, utils
from internship.models.enums.role_choice import ChoiceRole
from internship.models.score_encoding_utils import DEFAULT_PERIODS
from internship.services.utils import get_first_paginated_result, get_paginated_results

PAGINATION_SIZE = 100


class InternshipAPIClient:

    def __new__(cls):
        api_config = internship_sdk.build_configuration()
        return internship_api.InternshipApi(ApiClient(configuration=api_config))


class InternshipServiceException(ApiException):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class InternshipAPIService:
    @classmethod
    def get_master(cls, person):
        return get_first_paginated_result(
            InternshipAPIClient().masters_get(
                search=person.email, **utils.build_mandatory_auth_headers(person)
            )
        )

    @classmethod
    def activate_master_account(cls, person, master_uuid):
        return InternshipAPIClient().masters_uuid_activate_account_post(
            uuid=master_uuid, **utils.build_mandatory_auth_headers(person)
        )

    @classmethod
    def get_master_allocations(cls, person, master_uuid=None):
        return get_paginated_results(
            InternshipAPIClient().masters_uuid_allocations_get(
                uuid=master_uuid, current=True, **utils.build_mandatory_auth_headers(person)
            )
        )

    @classmethod
    def get_mastered_allocations(cls, person, specialty_uuid, organization_uuid):
        return get_paginated_results(
            InternshipAPIClient().masters_allocations_get(
                specialty=specialty_uuid, organization=organization_uuid, role=ChoiceRole.MASTER.name,
                **utils.build_mandatory_auth_headers(person)
            )
        )

    @classmethod
    def get_delegated_allocations(cls, person, specialty_uuid, organization_uuid):
        return get_paginated_results(
            InternshipAPIClient().masters_allocations_get(
                specialty=specialty_uuid, organization=organization_uuid, role=ChoiceRole.DELEGATE.name,
                **utils.build_mandatory_auth_headers(person)
            )
        )

    @classmethod
    def get_specialty(cls, person, specialty_uuid):
        return InternshipAPIClient().specialties_uuid_get(
            uuid=specialty_uuid, **utils.build_mandatory_auth_headers(person)
        )

    @classmethod
    def get_organization(cls, person, organization_uuid) -> OrganizationGet:
        return InternshipAPIClient().organizations_uuid_get(
            uuid=organization_uuid, **utils.build_mandatory_auth_headers(person)
        )

    @classmethod
    def get_students_affectations_count(cls, person, specialty_uuid, organization_uuid):
        return InternshipAPIClient().students_affectations_specialty_organization_stats_get(
            specialty=specialty_uuid, organization=organization_uuid, **utils.build_mandatory_auth_headers(person)
        )

    @classmethod
    def get_paginated_students_affectations(cls, person, specialty_uuid, organization_uuid, period, **kwargs):
        response = cls.get_students_affectations(person, specialty_uuid, organization_uuid, period, **kwargs)
        next = urlparse(response['next']).query if response['next'] else ''
        previous = urlparse(response['previous']).query if response['previous'] else ''
        results = get_paginated_results(response)
        count = response['count']
        return results, previous, next, count

    @classmethod
    def get_students_affectations(cls, person, specialty_uuid, organization_uuid, period=DEFAULT_PERIODS, **kwargs):
        return InternshipAPIClient().students_affectations_specialty_organization_get(
            specialty=specialty_uuid,
            organization=organization_uuid,
            period=period,
            **utils.build_mandatory_auth_headers(person),
            **kwargs
        )

    @classmethod
    def get_affectation(cls, person, affectation_uuid):
        return InternshipAPIClient().students_affectations_affectation_uuid_get(
            affectation_uuid=affectation_uuid, **utils.build_mandatory_auth_headers(person)
        )

    @classmethod
    def get_active_period(cls, person):
        return get_first_paginated_result(
            InternshipAPIClient().periods_get(
                active=True, **utils.build_mandatory_auth_headers(person)
            )
        )

    @classmethod
    def get_score(cls, person, affectation_uuid):
        try:
            return InternshipAPIClient().scores_affectation_uuid_get(
                affectation_uuid, **utils.build_mandatory_auth_headers(person)
            )
        except ApiException:
            return None

    @classmethod
    def update_score(cls, person, affectation_uuid, score):
        data, status, headers = InternshipAPIClient().scores_affectation_uuid_put(
            affectation_uuid,
            score_get=score,
            _return_http_data_only=False,
            **utils.build_mandatory_auth_headers(person)
        )
        return status == 200

    @classmethod
    def post_master(cls, person, master):
        try:
            return InternshipAPIClient().masters_post(master_get=master, **utils.build_mandatory_auth_headers(person))
        except ApiException as e:
            raise InternshipServiceException(
                status=e.status,
                reason=json.loads(e.body)[0] if e.status == 400 else ''
            )

    @classmethod
    def post_master_allocation(cls, person, allocation):
        return InternshipAPIClient().masters_allocations_post(
            allocation_get=allocation, **utils.build_mandatory_auth_headers(person)
        )

    @classmethod
    def delete_master_allocation(cls, person, allocation_uuid):
        data, status, headers = InternshipAPIClient().masters_allocations_uuid_delete(
            uuid=allocation_uuid,
            _return_http_data_only=False,
            **utils.build_mandatory_auth_headers(person)
        )
        return status == 204

    @classmethod
    def validate_internship_score(cls, person, affectation_uuid):
        try:
            return InternshipAPIClient().scores_affectation_uuid_validate_post(
                affectation_uuid=affectation_uuid,
                _return_http_data_only=False,
                **utils.build_mandatory_auth_headers(person)
            )
        except ApiException as e:
            return e.body, e.status, e.headers

    @classmethod
    def get_person_affectations(cls, cohort, person):
        return get_paginated_results(
            InternshipAPIClient().person_affectations_cohort_person_uuid_get(
                cohort=cohort.name,
                person_uuid=str(person.uuid),
                **utils.build_mandatory_auth_headers(person)
            )
        )

    @classmethod
    def get_evaluation_items(cls, cohort, person):
        return get_paginated_results(
            InternshipAPIClient().place_evaluation_items_cohort_get(
                cohort=cohort.name,
                limit=PAGINATION_SIZE,
                **utils.build_mandatory_auth_headers(person),
            )
        )

    @classmethod
    def get_evaluation(cls, person, affectation):
        return InternshipAPIClient().place_evaluation_affectation_uuid_get(
            affectation_uuid=affectation.uuid,
            **utils.build_mandatory_auth_headers(person)
        )

    @classmethod
    def update_evaluation(cls, person, affectation, evaluation):
        return InternshipAPIClient().place_evaluation_affectation_uuid_put(
            affectation_uuid=affectation.uuid,
            place_evaluation_get=PlaceEvaluationGet(
                evaluation=evaluation,
            ),
            **utils.build_mandatory_auth_headers(person)
        )
