##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2016 Université catholique de Louvain (http://www.uclouvain.be)
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
from django import template
from django.contrib import messages

register = template.Library()


def _is_message_type(context, msg_type):
    request = context['request']
    msgs = messages.get_messages(request)
    return any(msg_type in m.tags for m in msgs)


@register.simple_tag(takes_context=True)
def as_messages_info(context):
    return _is_message_type(context, 'info')


@register.simple_tag(takes_context=True)
def as_messages_warning(context):
    return _is_message_type(context, 'warning')


@register.simple_tag(takes_context=True)
def as_messages_error(context):
    return _is_message_type(context, 'error')


@register.simple_tag(takes_context=True)
def as_messages_success(context):
    return _is_message_type(context, 'success')
