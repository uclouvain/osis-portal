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
from typing import Set, List

import requests
from django.conf import settings
from django.http import HttpResponseBadRequest
from django.utils.functional import cached_property
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


def api_paginated_response(func, default_limit=DEFAULT_API_LIMIT, offset=0):
    """A decorator that enables to retrieve paginated response given desired limit and offset"""
    @wraps(func)
    def wrapper(*args, **kwargs) -> PaginatedResponse:
        response = func(*args, limit=kwargs.pop('limit', default_limit), offset=kwargs.pop('offset', offset), **kwargs)
        return PaginatedResponse(response.results, response.count)
    return wrapper


def gather_all_api_paginated_results(func):
    """A decorator that enables to gather all paginated responses into a unique list of results"""
    @wraps(func)
    def wrapper(*args, **kwargs) -> PaginatedResponse:
        paginated_response = api_paginated_response(func)(*args, **kwargs)
        while len(paginated_response.results) < paginated_response.count:
            paginated_response.extend(api_paginated_response(
                func, offset=len(paginated_response.results)
            )(*args, **kwargs))
        return paginated_response
    return wrapper


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


class PaginatedResponse:
    results: List
    count: int

    def __init__(self, results: List, count: int):
        self.results = results
        self.count = count

    def extend(self, paginated_response: 'PaginatedResponse'):
        self.results.extend(paginated_response.results)


class ApiPaginationMixin:
    count: int = 0

    request = None
    api_call = None

    @property
    def limit(self):
        return int(self.request.GET.get('limit', DEFAULT_API_LIMIT))

    @property
    def offset(self):
        return int(self.request.GET.get('offset', 0))

    @property
    def search(self):
        return self.request.GET.get('search', '')

    @property
    def ordering(self):
        return self.request.GET.get('ordering', '')

    @cached_property
    def page_objects_list(self) -> List:
        paginated_response = self.api_call(**self.get_api_kwargs())
        self.count = paginated_response.count
        return paginated_response.results

    def get_context_data(self, *args, **kwargs):
        inherited_context = super().get_context_data(**kwargs) if hasattr(super(), 'get_context_data') else {}
        return {
            **inherited_context,
            'count': self.count,
            'objects_list': self.page_objects_list,
        }

    def get_api_kwargs(self):
        return {
            'person': self.request.user.person,
            'limit':  self.limit,
            'offset': self.offset,
            'search': self.search,
            'ordering': self.ordering
        }


class ApiRetrieveAllObjectsMixin(ApiPaginationMixin):

    def get_api_kwargs(self):
        kwargs = super().get_api_kwargs()
        kwargs.pop('offset')
        return kwargs
