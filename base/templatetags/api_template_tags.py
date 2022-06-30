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

DEFAULT_SELECTABLE_LIMITS = [10, 25, 50, 100]
DEFAULT_CONDENSED_PAGINATION_DELTA = 2


@register.inclusion_tag('api/pagination.html', takes_context=True)
def pagination(context, condensed=True, delta=DEFAULT_CONDENSED_PAGINATION_DELTA):
    pagination_limit = context.get('limit', DEFAULT_API_LIMIT)
    pages_count = ceil(context['count']/pagination_limit)
    requested_offset = int(context['request'].GET.get('offset', 0))
    pages = [
        {
            'number': page + 1,
            'limit': pagination_limit,
            'offset': str(pagination_limit * page),
            'active_page': pagination_limit * page == requested_offset,
        } for page in range(pages_count)
    ]

    context['pages'] = pages
    context['first_offset'] = 0
    context['last_offset'] = (pages_count-1) * pagination_limit
    context['next_offset'] = context['offset'] + context['limit']
    context['previous_offset'] = context['offset'] - context['limit']

    context['active_page_number'] = next((page['number'] for page in pages if page['active_page']), 1)

    if pages:
        context['visible_indices'] = compute_visible_indices(
            pages,
            context['active_page_number'],
            delta=delta if condensed else len(pages)
        )

    return context


def compute_visible_indices(pages, active_page, delta):
    visible_indices = [pages[0]['number'], *range(active_page-delta, active_page+delta+1), pages[-1]['number']]
    # show page indices when the gap is only 1 e.g. (1, 3, 5) -> (1, 2, 3, 4, 5)
    for i, index in enumerate(visible_indices):
        if i+1 <= len(visible_indices) - 1 and visible_indices[i+1] - visible_indices[i] == 2:
            visible_indices.insert(i+1, visible_indices[i]+1)
    return visible_indices


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
    context['start_index'] = min(context['count'], context['offset'] + 1)
    context['end_index'] = min(context['offset'] + context['limit'], context['count'])
    context['total_count'] = context['count']
    return context


@register.inclusion_tag('api/limit_selector.html', takes_context=True)
def limit_selector(context):
    context['current_limit'] = context['limit']
    context['limit_choices'] = DEFAULT_SELECTABLE_LIMITS
    return context
