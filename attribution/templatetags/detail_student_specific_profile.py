##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2020 Université catholique de Louvain (http://www.uclouvain.be)
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
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _

from attribution.business.student_specific_profile import get_type_peps, get_arrangements, get_guide

register = template.Library()


@register.filter
def type_peps(student_specific_profile):
    if student_specific_profile:
        return get_type_peps(student_specific_profile)
    return None


@register.filter
def arrangements_and_guide(student_specific_profile):
    if student_specific_profile:
        specific_profile_detail = _get_arrangements_list(student_specific_profile)
        guide = get_guide(student_specific_profile)
        if guide:
            specific_profile_detail += "{} : {}".format(_('Guide'), guide)
        return mark_safe("<p style='text-align:left' >"+specific_profile_detail+"</p>") if specific_profile_detail else None
    return None


def _get_arrangements_list(student_specific_profile):
    arrangements = get_arrangements(student_specific_profile)
    if len(arrangements) >= 1:
        specific_profile_detail = "{} :".format(_('Arrangements'))
        for arrangement in arrangements:
            specific_profile_detail += "<br>* {}".format(arrangement)
        return "{}<br>".format(specific_profile_detail)
    return ''
