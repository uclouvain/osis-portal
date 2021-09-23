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
from math import ceil

from django import template

from frontoffice.settings.osis_sdk.utils import DEFAULT_API_LIMIT

register = template.Library()


@register.inclusion_tag('api/pagination.html', takes_context=True)
def pagination(context):
    pages_count = ceil(context['count']/DEFAULT_API_LIMIT)
    pages = [
        {
            'number': page+1,
            'limit': DEFAULT_API_LIMIT,
            'offset': str(DEFAULT_API_LIMIT*page)
        } for page in range(0, pages_count)
    ]

    context['pages'] = pages
    context['limit'] = DEFAULT_API_LIMIT
    context['first_offset'] = 0
    context['last_offset'] = (pages_count-1) * DEFAULT_API_LIMIT

    return context


@register.inclusion_tag('api/search.html', takes_context=True)
def search(context):
    return context


@register.inclusion_tag('api/ordering.html', takes_context=True)
def ordering(context, api_field_name):
    context['ordering_field_name'] = api_field_name
    return context
