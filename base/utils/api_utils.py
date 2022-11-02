from functools import wraps
from typing import List, Dict

import requests
from django.conf import settings
from django.utils.functional import cached_property
from django.utils.translation import gettext

from frontoffice.settings.osis_sdk.utils import DEFAULT_API_LIMIT


def get_list_from_osis(url, **kwargs):
    header_to_get = {'Authorization': f'Token {settings.OSIS_PORTAL_TOKEN}'}
    response = requests.get(
        url=url,
        headers=header_to_get,
        params=kwargs,
    )
    return response.json()


def get_country_list_from_osis(**kwargs):
    return get_list_from_osis(settings.URL_COUNTRY_API, **kwargs)


def get_training_list_from_osis(**kwargs):
    return get_list_from_osis(settings.URL_TRAINING_API, **kwargs)


class PaginatedResponse:

    def __init__(self, results: List, count: int = 0, **extra):
        self.results = results
        self.count = count
        self.extra = extra

    def extend(self, paginated_response: 'PaginatedResponse'):
        self.results.extend(paginated_response.results)

    def get_extra(self, key):
        return self.extra.get(key)


class ApiPaginationMixin:

    request = None
    api_call = None
    pagination_limit = DEFAULT_API_LIMIT

    @property
    def limit(self) -> int:
        return int(self.request.GET.get('limit', self.pagination_limit))

    @property
    def offset(self) -> int:
        return int(self.request.GET.get('offset', 0))

    @property
    def search(self) -> str:
        return self.request.GET.get('search', '')

    @property
    def ordering(self) -> str:
        return self.request.GET.get('ordering', '')

    @property
    def count(self) -> int:
        return self.paginated_response.count

    @property
    def object_name_plural(self) -> str:
        return gettext('item(s)')

    @cached_property
    def paginated_response(self) -> PaginatedResponse:
        return self.api_call(**self.get_api_kwargs())

    @cached_property
    def page_objects_list(self) -> List:
        return self.paginated_response.results

    def get_context_data(self, *args, **kwargs) -> Dict:
        inherited_context = super().get_context_data(**kwargs) if hasattr(super(), 'get_context_data') else {}
        return {
            **inherited_context,
            'count': self.count,
            'objects_list': self.page_objects_list,
            'limit': self.limit,
            'offset': self.offset,
            'object_name_plural': self.object_name_plural,
        }

    def get_api_kwargs(self) -> Dict:
        return {
            'person': self.request.user.person,
            'limit':  self.limit,
            'offset': self.offset,
            'search': self.search,
            'ordering': self.ordering
        }


class ApiRetrieveAllObjectsMixin(ApiPaginationMixin):

    def get_api_kwargs(self) -> Dict:
        kwargs = super().get_api_kwargs()
        kwargs.pop('offset')
        return kwargs


def api_paginated_response(func, default_limit=DEFAULT_API_LIMIT, offset=0):
    """A decorator that enables to retrieve paginated response given desired limit and offset"""
    @wraps(func)
    def wrapper(*args, **kwargs) -> PaginatedResponse:
        response = func(*args, limit=kwargs.pop('limit', default_limit), offset=kwargs.pop('offset', offset), **kwargs)
        return PaginatedResponse(**{key: getattr(response, key) for key in response.attribute_map.keys()})
    return wrapper


def gather_all_api_paginated_results(func):
    """A decorator that enables to gather all paginated responses into a unique list of results"""
    @wraps(func)
    def wrapper(*args, **kwargs) -> PaginatedResponse:
        paginated_response = api_paginated_response(func)(*args, **kwargs)
        while len(paginated_response.results) < paginated_response.count:
            kwargs['offset'] = len(paginated_response.results)
            paginated_response.extend(api_paginated_response(func)(*args, **kwargs))
        return paginated_response
    return wrapper
