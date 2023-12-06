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
from enum import Enum
from functools import wraps
from typing import Set, Union

import requests
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.http import Http404, HttpResponseBadRequest, HttpResponseForbidden, HttpResponseNotFound
from rest_framework import status

DEFAULT_API_LIMIT = 25


def get_user_token(person, force_user_creation=False):
    response = requests.post(
        url=settings.URL_AUTH_API,
        headers={
            'Authorization': 'Token ' + settings.OSIS_PORTAL_TOKEN,
            **build_custom_headers(person)
        },
        json={
            'username': person.user.username,
            'force_user_creation': force_user_creation,
        }
    )
    if response.status_code == status.HTTP_200_OK:
        return response.json()['token']
    return ""


def build_custom_headers(person):
    return {
        'X-User-FirstName': person.first_name or '',
        'X-User-LastName': person.last_name or '',
        'X-User-Email': person.email or '',
        'X-User-GlobalID': person.global_id,
        'Accept-Language': person.language
    }


def build_mandatory_auth_headers(person):
    """
    Return mandatory headers used for ESBAuthentification
    """
    return {
        'accept_language': person.language or settings.LANGUAGE_CODE,
        'x_user_first_name': person.first_name or '',
        'x_user_last_name':  person.last_name or '',
        'x_user_email': person.user.email or '',
        'x_user_global_id': person.global_id,
    }


def convert_api_enum(api_enum_cls) -> Enum:
    return Enum(api_enum_cls.__name__, api_enum_cls.allowed_values[('value',)])  # type: ignore # use of functional API


def api_exception_handler(api_exception_cls):
    def api_exception_decorator(func):
        @wraps(func)
        def wrapped_function(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except api_exception_cls as api_exception:
                ApiExceptionHandler().handle(api_exception)
        return wrapped_function
    return api_exception_decorator


class ApiBusinessException(Exception):
    def __init__(self, status_code: Union[int, str], detail: str):
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
                for exception in exceptions:
                    if isinstance(exception, dict):
                        api_business_exceptions.add(ApiBusinessException(**exception))
                    else:
                        api_business_exceptions.add(ApiBusinessException(
                            status_code=str(exception),
                            detail=str(exception),
                        ))
            raise MultipleApiBusinessException(exceptions=api_business_exceptions)
        elif api_exception.status == HttpResponseForbidden.status_code:
            try:
                body_json = json.loads(api_exception.body)
                detail = body_json.get('detail')
            except (TypeError, json.JSONDecodeError):
                detail = ""
            raise PermissionDenied(detail)
        elif api_exception.status == HttpResponseNotFound.status_code:
            try:
                body_json = json.loads(api_exception.body)
                detail = body_json.get('detail')
            except (TypeError, json.JSONDecodeError):
                detail = ""
            raise Http404(detail)
        raise api_exception
