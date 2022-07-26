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
from typing import Callable

from dal import autocomplete
from django import http

from frontoffice.settings.osis_sdk.utils import DEFAULT_API_LIMIT


class APIPaginatedSelect2ListViewMixin(autocomplete.Select2ListView):
    get_list_method: Callable
    API_LIMIT: int = DEFAULT_API_LIMIT
    get_total_method: Callable

    @cached_property
    def total(self):
        return self.get_total_method(person=self.request.user.person, search=self.q)

    def get_list(self, offset=0):
        return self.get_list_method(person=self.request.user.person, search=self.q, offset=offset)

    def get(self, request, *args, **kwargs):
        page = int(request.GET.get('page', 1))
        offset = (page - 1) * self.API_LIMIT
        results = self.results(self.get_list(offset=offset))
        if self.q:
            results = self.autocomplete_results(results)
        return http.JsonResponse({
            'results': results,
            'pagination': {
                'more': offset < self.total
            }
        }, content_type='application/json')
