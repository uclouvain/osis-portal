##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2018 Université catholique de Louvain (http://www.uclouvain.be)
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
import io
import logging
import traceback

import requests
from django.conf import settings
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.parsers import JSONParser

REQUEST_HEADER = {'Authorization': 'Token ' + settings.OSIS_PORTAL_TOKEN}
API_URL = settings.URL_API_BASE_PERSON_ROLES
logger = logging.getLogger(settings.DEFAULT_LOGGER)


def get_user_roles(global_id):
    response = requests.get(
        url=API_URL % {'global_id': global_id},
        headers=REQUEST_HEADER
    )
    if response.status_code == status.HTTP_404_NOT_FOUND:
        return None
    elif response.status_code == status.HTTP_403_FORBIDDEN:
        raise PermissionDenied(response.json()['detail'] if response.content else '')
    return transform_response_to_data(response)


def get_managed_programs_as_dict(global_id):
    programs = dict()
    try:
        user_roles = get_user_roles(global_id).get('roles')
        if user_roles and user_roles.get('program_manager'):
            for program in user_roles.get('program_manager').get('scope'):
                acronym = program.get('acronym')
                year = program.get('year')
                if programs.get(year):
                    programs.get(year).append(acronym)
                else:
                    programs[year] = [acronym]
    except Exception:
        trace = traceback.format_exc()
        logger.error(trace)
    return programs


def transform_response_to_data(response):
    stream = io.BytesIO(response.content)
    data = JSONParser().parse(stream)
    return data
