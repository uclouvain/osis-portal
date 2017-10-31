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
from django.conf import settings

from base import models as mdl_base
from attribution import models as mdl_attribution
from osis_common.queue import queue_sender


def get_application_list(global_id, academic_year=None):
    """
        Return the list of attribution that a tutor have applied
    """
    if not academic_year:
        academic_year = get_application_year()

    attrib = mdl_attribution.attribution_new.find_by_global_id(global_id)
    if attrib:
        return _filter_by_years(attrib.applications, academic_year.year)
    return None


def get_attribution_vacant(global_id, learning_container_year):
    acronym = learning_container_year.acronym
    academic_year = learning_container_year.academic_year
    attribution_vacant = get_attributions_vacant_for_application(global_id, acronym, academic_year)
    if attribution_vacant:
        return attribution_vacant[0]
    return None


def get_attributions_vacant_for_application(global_id, acronym_filter, academic_year=None):
    """
        Return the list of attribution which can be applied by a tutor
    """
    if not academic_year:
        academic_year = get_application_year()

    attributions_vacant = _get_attributions_vacant_for_application(acronym_filter, academic_year)
    attributions_vacant = _mark_attribution_already_applied(attributions_vacant, global_id, academic_year)
    return attributions_vacant


def _get_attributions_vacant_for_application(acronym_filter, academic_year):
    attribution_vacant = {}
    learning_containers_year_ids = list(mdl_base.learning_container_year.search(acronym=acronym_filter,
                                                                           academic_year=academic_year) \
                                                                        .values_list('id', flat=True))
    l_component_years = mdl_base.learning_component_year.search(learning_container_year=learning_containers_year_ids) \
                                                       # .exclude(volume_declared_vacant__isnull=True)
    for l_component_year in l_component_years:
        key = l_component_year.learning_container_year.id
        attribution_vacant.setdefault(key, {
            'title': l_component_year.learning_container_year.title,
            'acronym': l_component_year.learning_container_year.acronym,
            'learning_container_year_id': l_component_year.learning_container_year.id,
            'team': False
        }).update({
            l_component_year.type: l_component_year.volume_declared_vacant
        })
    return list(attribution_vacant.values())


def _mark_attribution_already_applied(attributions_vacant, global_id, academic_year):
    applications = get_application_list(global_id, academic_year)
    for attribution in attributions_vacant:
        attribution['already_applied'] = next((True for application in applications if
                                               application.get('acronym') == attribution.get('acronym')), False) \
                                          if applications else False
    return attributions_vacant


def get_application_year():
    # Application year is always for next year
    return mdl_base.academic_year.find_next_academic_year()


def _filter_by_years(attribution_list, year):
    return [attribution for attribution in attribution_list if attribution.get('year') == year]


def create_application(global_id, application_to_add):
    attrib = mdl_attribution.attribution_new.find_by_global_id(global_id)
    if attrib:
        if not attrib.applications:
            attrib.applications = []
        attrib.applications.append(application_to_add)
        attrib.save()
    return False


def delete(global_id, application_id):
    attrib = mdl_attribution.attribution_new.find_by_global_id(global_id)
    if attrib:
        application_to_delete = next((application for application in attrib.applications
                                      if application.get('id') == application_id), None)
        _send_deletion_application_to_queue(application_to_delete)
        # Remove from json array
        attrib.applications = [application for application in attrib.applications if
                               application != application_to_delete]
        attrib.save()
        return True
    return False


def _send_deletion_application_to_queue(application):
    DELETE_OPERATION = "delete"
    queue_name = settings.QUEUES.get('QUEUES_NAME', {}).get('ATTRIBUTION')

    if queue_name:
        queue_sender.send_message(queue_name, {
          'operation': DELETE_OPERATION,
          **application
        })
