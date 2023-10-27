# -*- coding: utf-8 -*-
############################################################################
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
############################################################################
import json
import re

from django import template
from django.template.defaulttags import register as reg

register = template.Library()


@register.simple_tag()
def choice_for_offer(internship_choices, offer, internship):
    try:
        choice = next(
            choice for choice in internship_choices
            if choice.specialty.uuid == offer.speciality.uuid
            and choice.organization['uuid'] == offer.organization.uuid
            and choice.internship == internship.name
        )
        return str(choice.choice)
    except (StopIteration, ValueError):
        return None


@reg.filter
def get_item(dictionary, key):
    val = dictionary.get(key)
    return val if val else ""


@reg.filter
def get_attr(object, name):
    return getattr(object, name) if hasattr(object, name) else None


@reg.filter
def only_number(text):
    return re.findall(r'\d+', text)[0]


@reg.filter
def to_json(dict):
    return json.dumps(dict)
