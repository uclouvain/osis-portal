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

from django.conf import settings
from osis_internship_sdk.api.default_api import DefaultApi
from osis_internship_sdk.api_client import ApiClient
from osis_internship_sdk.configuration import Configuration
from osis_internship_sdk.rest import ApiException


class InternshipAPIClient:

    def __new__(cls):
        api_config = Configuration()
        api_config.api_key['Authorization'] = "Token "+settings.OSIS_PORTAL_TOKEN
        api_config.host = settings.URL_INTERNSHIP_API
        return DefaultApi(api_client=ApiClient(configuration=api_config))


def get_first_paginated_result(response):
    return response['results'][0] if response['count'] else None


def get_paginated_results(response):
    return response['results']


def get_master_by_email(email):
    return get_first_paginated_result(
        InternshipAPIClient().masters_get(search=email)
    )


def get_master_allocations(master_uuid=None):
    return get_paginated_results(
        InternshipAPIClient().masters_uuid_allocations_get(uuid=master_uuid, current=True)
    )


def get_specialty(specialty_uuid):
    return InternshipAPIClient().specialties_uuid_get(uuid=specialty_uuid)


def get_organization(organization_uuid):
    return InternshipAPIClient().organizations_uuid_get(uuid=organization_uuid)


def get_students_affectations(specialty_uuid, organization_uuid, period="", with_score=False):
    return get_paginated_results(
        InternshipAPIClient().students_affectations_specialty_organization_get(
            specialty=specialty_uuid,
            organization=organization_uuid,
            period=period,
            with_score=with_score
        )
    )


def get_affectation(affectation_uuid):
    return InternshipAPIClient().students_affectations_uuid_get(uuid=affectation_uuid)


def get_period(period_uuid):
    return InternshipAPIClient().periods_uuid_get(uuid=period_uuid)


def get_active_period():
    return get_first_paginated_result(
        InternshipAPIClient().periods_get(active=True)
    )


def get_score(student_uuid, period_uuid):
    try:
        return InternshipAPIClient().scores_student_uuid_period_uuid_get(
            student_uuid=student_uuid, period_uuid=period_uuid
        )
    except ApiException:
        return None


def update_score(student_uuid, period_uuid, score):
    return InternshipAPIClient().scores_student_uuid_period_uuid_put(
        student_uuid, period_uuid, score_get=score, async_req=True
    )
