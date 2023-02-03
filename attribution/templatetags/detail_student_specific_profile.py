##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2023 Université catholique de Louvain (http://www.uclouvain.be)
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
from django.utils.translation import gettext as _

from attribution.business.student_specific_profile import get_type_peps, get_arrangements, get_guide

register = template.Library()


@register.filter
def type_peps(student_specific_profile):
    if student_specific_profile:
        return get_type_peps(student_specific_profile)
    return None


@register.filter
def arrangements_and_guide(student_specific_profile, learning_unit_type):
    if student_specific_profile:
        specific_profile_detail_html_content = "<div class='peps-tooltip-content'>"
        specific_profile_detail_html_content += _get_arrangements_list(
            student_specific_profile, learning_unit_type.value
        )
        guide = get_guide(student_specific_profile)
        if guide:
            specific_profile_detail_html_content += f"</ul><b>{_('Guide')}</b> :<br/>{guide}"

        specific_profile_detail_html_content += "</div>"
        return (
            mark_safe(specific_profile_detail_html_content) if specific_profile_detail_html_content else None  # nosec
        )
    return None


def _get_arrangements_list(student_specific_profile, learning_unit_type: str):
    arrangements = get_arrangements(student_specific_profile, learning_unit_type)
    if len(arrangements) >= 1:
        specific_profile_detail = f"<b>{_('Arrangements')}:</b><ul>"
        for arrangement in arrangements:
            specific_profile_detail += f"<li>{arrangement}</li>"
        return f"</ul>{specific_profile_detail}"
    return ''
