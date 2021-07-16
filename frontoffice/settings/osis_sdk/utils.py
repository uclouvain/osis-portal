##############################################################################
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
##############################################################################
import json
from functools import wraps
from typing import Set

import requests
from django.conf import settings
from django.http import HttpResponseBadRequest
from rest_framework import status


def get_token_from_osis(username, force_user_creation=False):
    response = requests.post(
        url=settings.URL_AUTH_API,
        headers={'Authorization': 'Token ' + settings.OSIS_PORTAL_TOKEN},
        data={
            'username': username,
            'force_user_creation': force_user_creation
        }
    )
    if response.status_code == status.HTTP_200_OK:
        return response.json()['token']
    return ""


def api_exception_handler(api_exception_cls):
    def api_exception_decorator(func):
        @wraps(func)
        def wrapped_function(*args, **kwargs):
            try:
                func(*args, **kwargs)
            except api_exception_cls as api_exception:
                ApiExceptionHandler().handle(api_exception)
        return wrapped_function
    return api_exception_decorator


class ApiBusinessException(Exception):
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail
        super(ApiBusinessException, self).__init__()

    def __hash__(self):
        return hash(self.status_code)

    def __eq__(self, other):
        return self.__class__ == other.__class__ and self.status_code == other.status_code


class MultipleApiBusinessException(Exception):
    def __init__(self, exceptions: Set[ApiBusinessException]):
        self.exceptions = exceptions
        super(MultipleApiBusinessException, self).__init__()


class ApiExceptionHandler:
    def handle(self, api_exception):
        if api_exception.status == HttpResponseBadRequest.status_code:
            api_business_exceptions = set()

            body_json = json.loads(api_exception.body)
            for key, exceptions in body_json.items():
                api_business_exceptions |= {ApiBusinessException(**exception) for exception in exceptions}
            raise MultipleApiBusinessException(exceptions=api_business_exceptions)
        raise api_exception
