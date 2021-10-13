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
    pagination_limit = context.get('limit', DEFAULT_API_LIMIT)
    pages_count = ceil(context['count']/pagination_limit)
    pages = [
        {
            'number': page+1,
            'limit': pagination_limit,
            'offset': str(pagination_limit*page)
        } for page in range(0, pages_count)
    ]

    context['pages'] = pages
    context['first_offset'] = 0
    context['last_offset'] = (pages_count-1) * pagination_limit
    context['next_offset'] = context['offset'] + context['limit']
    context['previous_offset'] = context['offset'] - context['limit']

    return context


@register.inclusion_tag('api/search.html', takes_context=True)
def search(context):
    return context


@register.inclusion_tag('api/ordering.html', takes_context=True)
def ordering(context, column_name, api_field_name):
    context['column_name'] = column_name
    context['ordering_field_name'] = api_field_name
    context['ordering_parameters'] = context.request.GET.get('ordering', '').split(',')
    return context


@register.inclusion_tag('api/count.html', takes_context=True)
def count(context):
    context['start_index'] = context['offset']
    context['end_index'] = min(context['offset'] + context['limit'], context['count'])
    context['total_count'] = context['count']
    return context


@register.inclusion_tag('api/limit_selector.html', takes_context=True)
def limit_selector(context):
    context['current_limit'] = context['limit']
    context['limit_choices'] = [25, 50, 100]
    return context
