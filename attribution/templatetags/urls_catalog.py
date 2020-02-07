##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2018 Université catholique de Louvain (http://www.uclouvain.be)
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
from django.conf import settings

from base.models.enums import learning_unit_year_subtypes
from base.models.learning_unit_year import LearningUnitYear
from base.utils import string_utils

register = template.Library()


@register.filter
def get_url_learning_unit_year(learning_container_year_id):
    a_learning_unit_year = LearningUnitYear.objects.filter(
        learning_container_year=learning_container_year_id,
        subtype=learning_unit_year_subtypes.FULL
    ).first()
    if a_learning_unit_year and string_utils.is_string_not_null_empty(a_learning_unit_year.acronym):
        year = a_learning_unit_year.academic_year.year
        return settings.ATTRIBUTION_CONFIG.get('CATALOG_URL').format(year, a_learning_unit_year.acronym.lower())
    return None
