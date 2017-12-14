##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2017 Université catholique de Louvain (http://www.uclouvain.be)
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
from decimal import Decimal
from itertools import chain

import collections

from attribution.models.enums import function
from base import models as mdl_base
from attribution import models as mdl_attribution
from base.models.enums import learning_component_year_type
from base.business import learning_unit_year_with_context


NO_CHARGE = 0.0


def get_attribution_list(global_id, academic_year=None):
    if not academic_year:
        academic_year = mdl_base.academic_year.current_academic_year()

    attrib = mdl_attribution.attribution_new.find_by_global_id(global_id)
    if attrib and attrib.attributions:
        attributions = _filter_by_years(attrib.attributions, academic_year)
        attributions = _format_str_volume_to_decimal(attributions)
        attributions = _append_team_and_volume_declared_vacant(attributions, academic_year)
        attributions = _append_start_and_end_academic_year(attributions)
        return _order_by_acronym_and_function(attributions)
    return []


def get_volumes_total(attribution_list):
    volumes_total = collections.defaultdict(lambda: Decimal(0))
    for attribution in attribution_list:
        lecturing_volume = attribution.get(learning_component_year_type.LECTURING)
        if lecturing_volume:
            volumes_total[learning_component_year_type.LECTURING] += Decimal(lecturing_volume)
        practical_exercices_volume = attribution.get(learning_component_year_type.PRACTICAL_EXERCISES)
        if practical_exercices_volume:
            volumes_total[learning_component_year_type.PRACTICAL_EXERCISES] += Decimal(practical_exercices_volume)
    return dict(volumes_total)


def get_attribution_vacant_list(acronym_filter, academic_year):
    attribution_vacant = {}
    learning_containers_year_ids = list(mdl_base.learning_container_year.search(acronym=acronym_filter,
                                                                                academic_year=academic_year)\
                                                                        .filter(team=False)\
                                                                        .values_list('id', flat=True))
    l_component_years = mdl_base.learning_component_year.search(learning_container_year=learning_containers_year_ids) \
                                                        .exclude(volume_declared_vacant__isnull=True)
    for l_component_year in l_component_years:
        key = l_component_year.learning_container_year.id
        attribution_vacant.setdefault(key, {
            'title': l_component_year.learning_container_year.title,
            'acronym': l_component_year.learning_container_year.acronym,
            'learning_container_year_id': l_component_year.learning_container_year.id,
            'team': l_component_year.learning_container_year.team
        }).update({
            l_component_year.type: l_component_year.volume_declared_vacant
        })
    return list(attribution_vacant.values())


def get_attribution_vacant(learning_container_year):
    acronym = learning_container_year.acronym
    academic_year = learning_container_year.academic_year
    attribution_vacant = get_attribution_vacant_list(acronym, academic_year)
    if attribution_vacant:
        return attribution_vacant[0]
    return None


def _append_team_and_volume_declared_vacant(attribution_list, academic_year):
    acronym_list = [attribution.get('acronym') for attribution in attribution_list]
    l_container_ids = list(mdl_base.learning_container_year.search(acronym=acronym_list, academic_year=academic_year)
                                                           .values_list('id', flat=True))
    l_components = mdl_base.learning_component_year.search(learning_container_year=l_container_ids)

    for attribution in attribution_list:
        volumes_declared_vacant = _get_volume_declared_vacant(attribution, l_components)
        is_team = _get_is_team(attribution, l_components)
        attribution.update({
          'volume_lecturing_vacant': volumes_declared_vacant[learning_component_year_type.LECTURING],
          'volume_practical_exercices_vacant': volumes_declared_vacant[learning_component_year_type.PRACTICAL_EXERCISES],
          'team': is_team
        })
    return attribution_list


def _get_volume_declared_vacant(attribution, l_component_year_list):
    volumes_declared_vacant = {
        learning_component_year_type.LECTURING: NO_CHARGE,
        learning_component_year_type.PRACTICAL_EXERCISES: NO_CHARGE
    }
    for l_component_year in l_component_year_list:
        if l_component_year.learning_container_year.acronym == attribution.get('acronym') and \
           l_component_year.volume_declared_vacant is not None:
            volumes_declared_vacant[l_component_year.type] += l_component_year.volume_declared_vacant
    return volumes_declared_vacant


def _get_is_team(attribution, l_component_year_list):
    return next((l_component_year.learning_container_year.team for l_component_year in l_component_year_list if
                 l_component_year.learning_container_year.acronym == attribution.get('acronym')), False)


def _append_start_and_end_academic_year(attribution_list):
    years = list(chain.from_iterable((attribution.get('start_year'), attribution.get('end_year'))
                                     for attribution in attribution_list))
    ac_years = mdl_base.academic_year.search(year=years)

    for attribution in attribution_list:
        start_year = attribution.get('start_year')
        if start_year:
            attribution['start_academic_year'] = _get_academic_year_related(start_year, ac_years)
        end_year = attribution.get('end_year')
        if end_year:
            attribution['end_academic_year'] = _get_academic_year_related(end_year, ac_years)
    return attribution_list


def _get_academic_year_related(year, academic_years):
    return next((academic_year for academic_year in academic_years if academic_year.year == year ), None)


def _filter_by_years(attribution_list, academic_year):
    return [attribution for attribution in attribution_list if attribution.get('year') == academic_year.year]


def _order_by_acronym_and_function(attribution_list):
    """
        Sort the list by
         0. Acronym
         1. Function
        :param attribution_list: List of attributions to sort
        :return:
    """
    def _sort(key):
        acronym = key.get('acronym', '')
        function = key.get('function', '')
        return "%s %s" % (acronym, function)
    return sorted(attribution_list, key=lambda k: _sort(k))


def get_attribution_list_about_to_expire(global_id, academic_year=None):
    import attribution.business.tutor_application
    if not academic_year:
        academic_year = mdl_base.academic_year.current_academic_year()

    attribution_list = get_attribution_list(global_id, academic_year)
    application_list = attribution.business.tutor_application.get_application_list(global_id)
    if attribution_list:
        # Remove application which are not about to expire
        attribution_list = _filter_attribution_about_to_expire(attribution_list, academic_year)
        # Append attribution vacant for next academic year
        attribution_list = _resolve_attribution_vacant_next_year(attribution_list, academic_year)
        # Mark if the attribution can be renewable
        attribution_list = _append_is_renewable(attribution_list, application_list)
        return attribution_list
    return None


def _filter_attribution_about_to_expire(attribution_list, academic_year):
    return [attribution for attribution in attribution_list if
            attribution.get('end_year') == academic_year.year and
            attribution.get('function') in (function.CO_HOLDER, function.HOLDER)]


def _format_str_volume_to_decimal(attribution_list):
    for attribution in attribution_list:
        if learning_component_year_type.LECTURING in attribution:
            attribution[learning_component_year_type.LECTURING] = Decimal(attribution[learning_component_year_type.LECTURING])
        else:
            attribution[learning_component_year_type.LECTURING] = NO_CHARGE
        if learning_component_year_type.PRACTICAL_EXERCISES in attribution:
            attribution[learning_component_year_type.PRACTICAL_EXERCISES] = Decimal(attribution[learning_component_year_type.PRACTICAL_EXERCISES])
        else:
            attribution[learning_component_year_type.PRACTICAL_EXERCISES] = NO_CHARGE
    return attribution_list


def _resolve_attribution_vacant_next_year(attribution_list, academic_year):
    acronyms = [attribution.get('acronym') for attribution in attribution_list]
    next_year_academic_calendar = mdl_base.academic_year.find_by_year(academic_year.year + 1)

    if acronyms and next_year_academic_calendar:
        attrib_vacant_list = get_attribution_vacant_list(acronyms, next_year_academic_calendar)
        for attribution in attribution_list:
            attribution['attribution_vacant'] = next(
                (attrib_vacant for attrib_vacant in attrib_vacant_list
                 if attrib_vacant.get('acronym') == attribution.get('acronym')), None
            )

    return [attrib for attrib in attribution_list if attrib.get('attribution_vacant')]


def _append_is_renewable(attribution_with_vacant_list, application_list):
    for attribution in attribution_with_vacant_list:
        attribution['not_renewable_reason'] = _check_is_renewable(attribution, application_list)
        attribution['is_renewable'] = (attribution['not_renewable_reason'] is None)
    return attribution_with_vacant_list


def _check_is_renewable(attribution_with_vacant_next_year, application_list):
    """
    This function check if the volume of attribution [current year] is lower or equals to attribution vacant next year
    :param attribution_with_vacant_next_year:
    :param application_list:
    :return: error code if not valid, None if no error
    """
    next_year_attribution_vacant = attribution_with_vacant_next_year['attribution_vacant']

    current_volume_lecturing = attribution_with_vacant_next_year.get(learning_component_year_type.LECTURING, 0)
    current_volume_practical_exercices = attribution_with_vacant_next_year.get(learning_component_year_type.PRACTICAL_EXERCISES, 0)

    if current_volume_lecturing == current_volume_practical_exercices == 0:
        return 'cannot_renew_zero_volume'

    next_volume_lecturing = next_year_attribution_vacant.get(learning_component_year_type.LECTURING, 0)
    if current_volume_lecturing > next_volume_lecturing:
        return 'volume_next_year_lower_than_current'

    next_volume_practical_exercices = next_year_attribution_vacant.get(learning_component_year_type.PRACTICAL_EXERCISES, 0)
    if current_volume_practical_exercices > next_volume_practical_exercices:
        return 'volume_next_year_lower_than_current'

    if _has_already_applied(attribution_with_vacant_next_year, application_list):
        return 'already_applied'

    return None


def _has_already_applied(attribution_with_vacant_next_year, application_list):
    return any(application['acronym'] == attribution_with_vacant_next_year.get('acronym')
               for application in application_list)


def get_learning_unit_volume(an_attribution, application_year):
    learning_unit_year = mdl_base.learning_unit_year.find_first_by_exact_acronym(application_year,
                                                                                  an_attribution['acronym'])
    an_attribution['lecturing_vol'] = NO_CHARGE
    an_attribution['practical_exercises_vol'] = NO_CHARGE

    learning_units = learning_unit_year_with_context.get_with_context(learning_container_year_id=learning_unit_year.learning_container_year)
    for l in learning_units:
        for learning_component_yr in l.components:
            if learning_component_yr.type == learning_component_year_type.LECTURING:
                an_attribution['lecturing_vol'] = _calculate_effective_volume(l.components[learning_component_yr])
            if learning_component_yr.type == learning_component_year_type.PRACTICAL_EXERCISES:
                an_attribution['practical_exercises_vol'] = _calculate_effective_volume(l.components[learning_component_yr])
        break


def _calculate_effective_volume(data):
    if 'VOLUME_TOTAL' in data and 'PLANNED_CLASSES' in data \
            and _is_positive(data['VOLUME_TOTAL']) and _is_positive(data['PLANNED_CLASSES']):
        return data['VOLUME_TOTAL'] * data['PLANNED_CLASSES']
    return NO_CHARGE


def _is_positive(value):
    if value > 0:
        return True
    return False
