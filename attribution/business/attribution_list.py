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

from base import models as mdl_base
from attribution import models as mdl_attribution
from base.models.enums import learning_component_year_type


def get_attribution_list(global_id, academic_year=None):
    if not academic_year:
        academic_year = mdl_base.academic_year.current_academic_year()

    attrib = mdl_attribution.attribution_new.find_by_global_id(global_id)
    if attrib:
        attributions = _filter_by_years(attrib.attributions, academic_year.year)
        return _order_by_acronym_and_function(attributions)
    return None


def get_volumes_total(attribution_list):
    volumes_total = {}
    for attribution in attribution_list:
        lecturing_volume = attribution.get(learning_component_year_type.LECTURING)
        if lecturing_volume:
            volumes_total.setdefault(learning_component_year_type.LECTURING, Decimal(0))
            volumes_total[learning_component_year_type.LECTURING] += Decimal(lecturing_volume)
        practical_exercices_volume = attribution.get(learning_component_year_type.PRACTICAL_EXERCISES)
        if practical_exercices_volume:
            volumes_total.setdefault(learning_component_year_type.PRACTICAL_EXERCISES, Decimal(0))
            volumes_total[learning_component_year_type.PRACTICAL_EXERCISES] += Decimal(practical_exercices_volume)
    return volumes_total


def append_team_and_volume_declared_vacant(attribution_list):
    acronym_list = [attribution.get('acronym') for attribution in attribution_list]
    l_container_ids = list(mdl_base.learning_container_year.search(acronym=acronym_list).values_list('id', flat=True))
    l_components = mdl_base.learning_component_year.search(learning_container_year=l_container_ids)

    for attribution in attribution_list:
        volumes_declared_vacant = _get_volume_declared_vacant(attribution, l_components)
        attribution.update({
          'volume_lecturing_vacant': volumes_declared_vacant[learning_component_year_type.LECTURING],
          'volume_practical_exercices_vacant': volumes_declared_vacant[learning_component_year_type.PRACTICAL_EXERCISES],
          'team': True
        })
    return attribution_list


def _get_volume_declared_vacant(attribution, l_component_year_list):
    volumes_declared_vacant = {
        learning_component_year_type.LECTURING: Decimal(0),
        learning_component_year_type.PRACTICAL_EXERCISES: Decimal(0)
    }
    for l_component_year in l_component_year_list:
        if l_component_year.learning_container_year.acronym == attribution.get('acronym') and \
           l_component_year.volume_declared_vacant is not None:
            volumes_declared_vacant[l_component_year.type] += l_component_year.volume_declared_vacant
    return volumes_declared_vacant


def append_start_and_end_academic_year(attribution_list):
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


def _filter_by_years(attribution_list, year):
    return [attribution for attribution in attribution_list if attribution.get('year') == year]


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

