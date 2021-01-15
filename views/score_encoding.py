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
from django.contrib.auth.decorators import login_required

from base.views import layout
from internship.views.api_client import InternshipAPIClient, get_paginated_results, get_first_paginated_result


@login_required(login_url="/internship/auth/login/")
def view_score_encoding(request):
    master = _get_master_by_email(request.user.username)
    allocations = _get_master_allocations(master['uuid'])
    return layout.render(request, "internship_score_encoding.html", locals())


@login_required(login_url="/internship/auth/login/")
def view_score_encoding_sheet(request, specialty_uuid, organization_uuid):
    specialty = _get_specialty(specialty_uuid)
    organization = _get_organization(organization_uuid)
    students_affectations = _get_students_affectations(specialty_uuid, organization_uuid)
    return layout.render(request, "internship_score_encoding_sheet.html", locals())


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


def _get_students_affectations(specialty_uuid, organization_uuid):
    return get_paginated_results(
        InternshipAPIClient().students_affectations_get(specialty=specialty_uuid, organization=organization_uuid)
    )