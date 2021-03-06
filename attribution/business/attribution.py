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
import collections
from collections import OrderedDict
from decimal import Decimal
from itertools import chain

from django.db.models import OuterRef, Subquery
from django.utils.translation import ugettext_lazy as _

from attribution import models as mdl_attribution
from attribution.models.enums import function
from base import models as mdl_base
from base.business import learning_unit_year_with_context
from base.business.entity import get_entities_ids
from base.models.entity_version import EntityVersion
from base.models.enums.learning_container_type import IN_CHARGE_TYPES
from base.models.enums import learning_component_year_type
from base.models.enums import vacant_declaration_type
from base.models.learning_component_year import LearningComponentYear
from base.models.person import Person
from base.models.enums.learning_component_year_type import LECTURING, PRACTICAL_EXERCISES

NO_CHARGE = 0.0

PERSON_KEY = 'person'


def get_attribution_list(global_id, academic_year):
    attribution_new = mdl_attribution.attribution_new.find_by_global_id(global_id)
    if attribution_new and attribution_new.attributions:
        attributions = _filter_by_years(attribution_new.attributions, academic_year)
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


def get_attribution_vacant_list(acronym_filter, academic_year, faculty=None):
    attribution_vacant = OrderedDict()

    learning_components = _get_learning_components(
        academic_year,
        acronym_filter,
        faculty
    )
    for l_component_year in learning_components:
        container = l_component_year.learning_unit_year.learning_container_year
        key = container.id
        attribution_vacant.setdefault(key, {
            'title': l_component_year.learning_unit_year.complete_title,
            'acronym': container.acronym,
            'learning_container_year_id': container.id,
            'team': container.team
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
    l_components = LearningComponentYear.objects.filter(
        learning_unit_year__learning_container_year__in=l_container_ids,
        type__in=[LECTURING, PRACTICAL_EXERCISES]
    ).select_related('learning_unit_year__learning_container_year')

    for attribution in attribution_list:
        volumes_declared_vacant = _get_volume_declared_vacant(attribution, l_components)
        is_team = _get_is_team(attribution, l_components)
        attribution.update({
            'volume_lecturing_vacant': volumes_declared_vacant[learning_component_year_type.LECTURING],
            'volume_practical_exercices_vacant': volumes_declared_vacant[
                learning_component_year_type.PRACTICAL_EXERCISES],
            'team': is_team
        })
    return attribution_list


def _get_volume_declared_vacant(attribution, l_component_year_list):
    volumes_declared_vacant = {
        learning_component_year_type.LECTURING: Decimal(0),
        learning_component_year_type.PRACTICAL_EXERCISES: Decimal(0)
    }
    for l_component_year in l_component_year_list:
        if l_component_year.learning_unit_year.learning_container_year.acronym == attribution.get('acronym') and \
                l_component_year.volume_declared_vacant is not None:
            volumes_declared_vacant[l_component_year.type] += l_component_year.volume_declared_vacant
    return volumes_declared_vacant


def _get_is_team(attribution, l_component_year_list):
    return next(
        (
            l_component_year.learning_unit_year.learning_container_year.team
            for l_component_year in l_component_year_list if
            l_component_year.learning_unit_year.learning_container_year.acronym == attribution.get('acronym')
        ),
        False
    )


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
    return next((academic_year for academic_year in academic_years if academic_year.year == year), None)


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


def get_attribution_list_about_to_expire(global_id, academic_year):
    import attribution.business.tutor_application

    attribution_list = get_attribution_list(global_id, academic_year)
    application_list = attribution.business.tutor_application.get_application_list(global_id, academic_year)
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
            attribution[learning_component_year_type.LECTURING] = Decimal(
                attribution[learning_component_year_type.LECTURING])
        else:
            attribution[learning_component_year_type.LECTURING] = NO_CHARGE
        if learning_component_year_type.PRACTICAL_EXERCISES in attribution:
            attribution[learning_component_year_type.PRACTICAL_EXERCISES] = Decimal(
                attribution[learning_component_year_type.PRACTICAL_EXERCISES])
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
    next_year_attribution_vacant = attribution_with_vacant_next_year['attribution_vacant']

    current_volume_lecturing = attribution_with_vacant_next_year.get(learning_component_year_type.LECTURING, NO_CHARGE)
    current_volume_practical_exercices = attribution_with_vacant_next_year.get(
        learning_component_year_type.PRACTICAL_EXERCISES, NO_CHARGE)

    next_volume_lecturing = next_year_attribution_vacant.get(learning_component_year_type.LECTURING, NO_CHARGE)
    next_volume_practical_exercices = next_year_attribution_vacant.get(learning_component_year_type.PRACTICAL_EXERCISES,
                                                                       NO_CHARGE)
    if next_volume_lecturing == 0 and next_volume_practical_exercices == 0:
        return _('No vacant corresponding activity')

    if current_volume_lecturing > next_volume_lecturing or \
            current_volume_practical_exercices > next_volume_practical_exercices:
        return _('The vacant volume of the next academic year is lower than the current one')

    if _has_already_applied(attribution_with_vacant_next_year, application_list):
        return _('An application has already been submitted')

    if attribution_with_vacant_next_year['is_substitute']:
        return _('A substitute can not renew his function of substitute')

    if _is_managed_in_team(next_year_attribution_vacant["learning_container_year_id"]):
        return _('This course is team-managed. The application to this activity is based on a paper transmission.')

    return None


def _is_managed_in_team(learning_container_year_id):
    l_container_year = mdl_base.learning_container_year.LearningContainerYear.objects.get(
        id=learning_container_year_id
    )
    return l_container_year.team


def _has_already_applied(attribution_with_vacant_next_year, application_list):
    return any(application['acronym'] == attribution_with_vacant_next_year.get('acronym')
               for application in application_list)


def update_learning_unit_volume(an_attribution, application_year):
    an_attribution['lecturing_vol'] = NO_CHARGE
    an_attribution['practical_exercises_vol'] = NO_CHARGE

    learning_unit_year = mdl_base.learning_unit_year.find_first_by_exact_acronym(application_year,
                                                                                 an_attribution['acronym'])
    l_container_year = learning_unit_year.learning_container_year
    learning_units = learning_unit_year_with_context.get_with_context(learning_container_year_id=l_container_year)
    if learning_units:
        _calculate_component_volume(an_attribution, learning_units[0].components)


def _calculate_component_volume(an_attribution, components):
    for learning_component_yr, volume_data in components.items():
        if learning_component_yr.type == learning_component_year_type.LECTURING:
            an_attribution['lecturing_vol'] = _calculate_effective_volume(volume_data)
        if learning_component_yr.type == learning_component_year_type.PRACTICAL_EXERCISES:
            an_attribution['practical_exercises_vol'] = _calculate_effective_volume(volume_data)


def _calculate_effective_volume(data):
    if 'VOLUME_TOTAL' in data and 'PLANNED_CLASSES' in data \
            and data['VOLUME_TOTAL'] > 0 and data['PLANNED_CLASSES'] > 0:
        return data['VOLUME_TOTAL'] * data['PLANNED_CLASSES']
    return NO_CHARGE


def get_teachers(learning_unit_acronym, application_yr):
    if learning_unit_acronym and application_yr:
        teachers = mdl_attribution.attribution_new.find_teachers(learning_unit_acronym, application_yr)
        if teachers:
            teachers_data = _find_teachers_with_person(application_yr, learning_unit_acronym, teachers)
            return sorted(teachers_data, key=lambda teacher: str(teacher[PERSON_KEY]))
    return None


def _find_teachers_with_person(application_yr, learning_unit_acronym, teachers):
    teachers_data = []
    global_ids = [teacher.global_id for teacher in teachers]
    person_list = Person.objects.filter(global_id__in=global_ids) if global_ids else None
    for teacher in teachers:
        for an_attribution in teacher.attributions:
            if an_attribution['acronym'] == learning_unit_acronym and an_attribution['year'] == application_yr:
                an_attribution[PERSON_KEY] = next(
                    (person for person in person_list if person.global_id == teacher.global_id))
                teachers_data.append(an_attribution)

    return teachers_data if len(teachers_data) > 0 else None


def get_filter_learning_container_ids(entity_version, qs):
    """
    Append a filter on the queryset if entities are given in the search

    :param qs: LearningUnitYearQuerySet
    :return: queryset
    """

    if entity_version:
        allocation_entity_ids = get_entities_ids(entity_version.acronym, True)
        qs = qs.filter(
            learning_container_year__allocation_entity__in=allocation_entity_ids
        )

    return qs


def _get_learning_components(academic_year, acronym_filter, faculty):
    type_declaration_vacant_allowed = [vacant_declaration_type.RESERVED_FOR_INTERNS,
                                       vacant_declaration_type.OPEN_FOR_EXTERNS]

    if faculty:
        learning_components = _get_learning_components_by_faculty(academic_year, acronym_filter, faculty)
    else:
        learning_container_yrs = mdl_base.learning_container_year.search(
            acronym=acronym_filter,
            academic_year=academic_year
        )
        learning_components = LearningComponentYear.objects \
            .filter(learning_unit_year__learning_container_year_id__in=learning_container_yrs) \
            .filter(learning_unit_year__learning_container_year__container_type__in=IN_CHARGE_TYPES) \
            .order_by('learning_unit_year__acronym') \
            .select_related('learning_unit_year__learning_container_year') \
            .exclude(volume_declared_vacant__isnull=True)
    return learning_components.filter(
        learning_unit_year__learning_container_year__type_declaration_vacant__in=type_declaration_vacant_allowed
    )


def _get_learning_components_by_faculty(academic_year, acronym_filter, faculty):
    entity_allocation = EntityVersion.objects.filter(
        entity=OuterRef('learning_container_year__allocation_entity'),
    ).current(
        OuterRef('academic_year__start_date')
    ).values('acronym')[:1]
    learning_unit_years = mdl_base.learning_unit_year.search(acronym=acronym_filter, academic_year_id=academic_year)
    learning_unit_years = learning_unit_years.select_related(
        'academic_year', 'learning_container_year__academic_year'
    ).order_by('academic_year__year', 'acronym').annotate(
        entity_allocation=Subquery(entity_allocation),
    )
    learning_unit_years = get_filter_learning_container_ids(faculty, learning_unit_years)
    learning_unit_years_ids = learning_unit_years.values_list('id', flat=True)
    return LearningComponentYear.objects \
        .filter(learning_unit_year_id__in=learning_unit_years_ids) \
        .select_related('learning_unit_year__learning_container_year') \
        .exclude(volume_declared_vacant__isnull=True) \
        .order_by('learning_unit_year__acronym')
