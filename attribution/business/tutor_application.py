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
import datetime
from decimal import Decimal

from django.db import transaction
from attribution import models as mdl_attribution
from base import models as mdl_base
from base.models.enums import learning_unit_year_subtypes


def get_application_list(global_id, academic_year):
    """
    Return the list of attribution that a tutor have applied in a specific academic year
    """
    attrib = mdl_attribution.attribution_new.find_by_global_id(global_id)
    if attrib and attrib.applications:
        application_list = list(_filter_by_years(attrib.applications, academic_year.year))
        application_list = _format_str_volume_to_decimal(application_list)
        application_list = _resolve_learning_container_year_info(application_list, academic_year)
        return _order_by_pending_and_acronym(application_list)
    return []


def validate_application(global_id, acronym, year):
    academic_year = mdl_base.academic_year.find_by_year(year)
    application_list = get_application_list(global_id, academic_year)

    application = _find_application(acronym, year, application_list)
    if application:
        application.pop('pending', None)
        _update_application(global_id, application)


def delete_application(global_id, acronym, year):
    attrib = mdl_attribution.attribution_new.find_by_global_id(global_id)
    if attrib and attrib.applications:
        attrib.applications = _delete_application_in_list(acronym, year, attrib.applications)
        attrib.save()
        return True
    return False


def _resolve_learning_container_year_info(application_list, academic_year):
    acronym_list = [application.get('acronym') for application in application_list]
    l_container_years = mdl_base.learning_container_year.search(
        acronym=acronym_list,
        academic_year=academic_year
    ).prefetch_related('learningunityear_set__learningcomponentyear_set')
    for application in application_list:
        l_container_year = next((l_container_year for l_container_year in l_container_years if
                                 l_container_year.acronym == application.get('acronym')), None)
        if l_container_year:
            _modify_application(application, l_container_year)
    return application_list


def _modify_application(application, l_container_year):
    application['learning_container_year_id'] = l_container_year.id
    learning_unit_year_full = next(luy for luy in l_container_year.learningunityear_set.all()
                                   if luy.subtype == learning_unit_year_subtypes.FULL)
    application['title'] = learning_unit_year_full.complete_title
    for l_component_year in learning_unit_year_full.learningcomponentyear_set.all():
        application[l_component_year.type] = l_component_year.volume_declared_vacant


def _update_application(global_id, application_to_update):
    with transaction.atomic():
        attrib = mdl_attribution.attribution_new.AttributionNew.objects.select_for_update().filter(
            global_id=global_id,
        ).first()
        if not attrib:
            return None

        acronym = application_to_update.get('acronym')
        year = application_to_update.get('year')

        # Remove and append new records to json array
        attrib.applications = _delete_application_in_list(acronym, year, attrib.applications)
        application_to_update['updated_at'] = _get_serialized_time()
        attrib.applications.append(application_to_update)

        return attrib.save()


def _delete_application_in_list(acronym, year, application_list):
    return [application for application in application_list if
            not (acronym == application.get('acronym') and year == application.get('year'))]


def _find_application(acronym, year, applications_list):
    if applications_list:
        return next((application for application in applications_list
                     if application.get('year') == year and application.get('acronym') == acronym),
                    None)
    return None


def _filter_by_years(attribution_list, year):
    for attribution in attribution_list:
        if attribution.get('year') == year:
            yield attribution


def _get_serialized_time() -> str:
    return str(datetime.datetime.now())


def _order_by_pending_and_acronym(application_list):
    """
        Sort the list by
         0. Pending
         1. Acronym
        :param application_list: List of application to sort
        :return:
    """

    def _sort(key):
        pending = key.get('pending', '')
        acronym = key.get('acronym', '')
        return "%s %s" % (pending, acronym)

    return sorted(application_list, key=lambda k: _sort(k))


def _format_str_volume_to_decimal(application_list):
    for application in application_list:
        if 'charge_lecturing_asked' in application:
            application['charge_lecturing_asked'] = \
                Decimal(application['charge_lecturing_asked'] if application['charge_lecturing_asked'] else 0.0)
        if 'charge_practical_asked' in application:
            application['charge_practical_asked'] = \
                Decimal(application['charge_practical_asked'] if application['charge_practical_asked'] else 0.0)
    return application_list
