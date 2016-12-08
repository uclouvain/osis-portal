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
from attribution import models as mdl_attribution
from attribution.views import teaching_load
from base import models as mdl_base
from base.models.enums import component_type


ACRONYM = 'acronym'
TITLE = 'title'
LECTURING_DURATION = 'lecturing_duration'
PRACTICAL_DURATION = 'practice_duration'
START = 'start'
END = 'end'
ATTRIBUTION_CHARGE_LECTURING = 'attribution_charge_lecturing'
ATTRIBUTION_CHARGE_PRACTICAL = 'attribution_charge_practical'
FUNCTION = 'function'

TWO_DECIMAL_FORMAT = "%0.2f"


def get_attributions_allocated(a_year, a_tutor):
    attributions_results = []
    an_academic_year = mdl_base.academic_year.find_by_year(a_year)
    if a_tutor and an_academic_year:
        attributions = mdl_attribution.attribution.find_by_tutor_year_order_by_acronym_fonction(a_tutor, an_academic_year)
        for attribution in attributions:
            attributions_results.append(
            {ACRONYM: attribution.learning_unit_year.acronym,
             TITLE: attribution.learning_unit_year.title,
             LECTURING_DURATION: format_duration(get_learning_unit_component_duration(attribution.learning_unit_year, component_type.LECTURING)),
             PRACTICAL_DURATION: format_duration(get_learning_unit_component_duration(attribution.learning_unit_year, component_type.PRACTICAL_EXERCISES)),
             START: attribution.start_date.year,
             END: attribution.end_date.year,
             ATTRIBUTION_CHARGE_LECTURING:
                 format_duration(teaching_load.get_attribution_allocation_charge(a_tutor,
                                                                                 attribution.learning_unit_year,
                                                                                 component_type.LECTURING)),
             ATTRIBUTION_CHARGE_PRACTICAL:
                 format_duration(teaching_load.get_attribution_allocation_charge(a_tutor,
                                                                                 attribution.learning_unit_year,
                                                                                 component_type.PRACTICAL_EXERCISES)),
             FUNCTION: attribution.function})
    print(attributions_results)
    return attributions_results


def get_learning_unit_component_duration(a_learning_unit_year, a_component_type):
    a_learning_unit_components = mdl_base.learning_unit_component.search(a_learning_unit_year, a_component_type)
    tot_duration = 0
    for a_learning_unit_component in a_learning_unit_components:
        tot_duration += a_learning_unit_component.duration
    return tot_duration


def format_duration(duration):
    return TWO_DECIMAL_FORMAT % (duration,)