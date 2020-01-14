##############################################################################
#
# OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2020 Université catholique de Louvain (http://www.uclouvain.be)
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

import requests
from django.conf import settings
from rest_framework import status
from rest_framework.parsers import JSONParser

from frontoffice.settings.base import URL_LEARNING_UNIT_ENROLLMENT_API

logger = logging.getLogger(settings.DEFAULT_LOGGER)
queue_exception_logger = logging.getLogger(settings.QUEUE_EXCEPTION_LOGGER)


REQUEST_HEADER = {'Authorization': 'Token ' + settings.OSIS_PORTAL_TOKEN}


def _get_token_from_osis(username, force_user_creation=False):
    response = requests.post(
        url=settings.URL_AUTH_API,
        headers=REQUEST_HEADER,
        data={
            'username': username,
            'force_user_creation': force_user_creation
        }
    )
    if response.status_code == status.HTTP_200_OK:
        return response.json()['token']
    else:
        return ""


def _get_personal_token(request):
    if not request.session.get('personal_token'):
        request.session['personal_token'] = _get_token_from_osis(request.user.username, force_user_creation=True)
    return request.session['personal_token']


def _transform_response_to_data(response):
    stream = io.BytesIO(response.content)
    data = JSONParser().parse(stream)
    return data


# TODO :: replace with LearningUnitEnrollment API (SDK)
def enrollments_list_by_student(request, registration_id):
    token = _get_personal_token(request)
    api_url = URL_LEARNING_UNIT_ENROLLMENT_API + "%(registration_id)s/"
    url = api_url % {'registration_id': registration_id}
    response = requests.get(
        url=url,
        headers={'Authorization': 'Token ' + token}
    )
    return _transform_response_to_data(response)


# TODO :: replace with LearningUnitEnrollment API (SDK)
def enrollments_list_by_learning_unit(request, year, acronym, offer_enrollment_states):
    api_url = URL_LEARNING_UNIT_ENROLLMENT_API + "learning_units/%(year)s/%(acronym)s/enrollments/"
    token = _get_personal_token(request)
    url = api_url % {
        'year': year,
        'acronym': acronym,
    }
    response = requests.get(
        url=url,
        params={
            'limit': 1000,
            'offset': 0,
            'offer_enrollment_state': ','.join(offer_enrollment_states)
        },
        headers={'Authorization': 'Token ' + token}
    )
    return _transform_response_to_data(response)
