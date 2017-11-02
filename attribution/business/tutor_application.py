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
from django.utils.translation import ugettext_lazy as _

from base import models as mdl_base
from attribution import models as mdl_attribution
from base.models.enums import learning_component_year_type
from osis_common.messaging import message_config, send_message as message_service
from osis_common.queue import queue_sender


def get_application_list(global_id, academic_year=None):
    """
        Return the list of attribution that a tutor have applied
    """
    if not academic_year:
        academic_year = get_application_year()

    attrib = mdl_attribution.attribution_new.find_by_global_id(global_id)
    if attrib and attrib.applications:
        attrib.applications = _filter_by_years(attrib.applications, academic_year.year)
        return _resolve_learning_container_year_info(attrib.applications, academic_year)
    return None


def find_application(global_id, learning_container_year):
    application_list = get_application_list(global_id, learning_container_year.academic_year)
    return _find_application(learning_container_year.acronym, learning_container_year.academic_year.year ,
                             application_list)


def _resolve_learning_container_year_info(application_list, academic_year):
    acronym_list = [application.get('acronym') for application in application_list]
    l_container_years = mdl_base.learning_container_year.search(acronym=acronym_list, academic_year=academic_year)\
                                                        .prefetch_related('learningcomponentyear_set')
    for application in application_list:
        l_container_year = next((l_container_year for l_container_year in l_container_years if
                                 l_container_year.acronym == application.get('acronym')),None)
        application['learning_container_year_id'] = l_container_year.id
        application['title'] = l_container_year.title
        for l_component_year in l_container_year.learningcomponentyear_set.all():
            application[l_component_year.type] = 40#l_component_year.volume_declared_vacant
    return application_list


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
            l_component_year.type: 30, #l_component_year.volume_declared_vacant
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
    return mdl_base.academic_year.current_academic_year()   # mdl_base.academic_year.find_next_academic_year()


def _filter_by_years(attribution_list, year):
    return [attribution for attribution in attribution_list if attribution.get('year') == year]


def create_or_update_application(global_id, application):
    attrib = mdl_attribution.attribution_new.find_by_global_id(global_id)
    if attrib:
        acronym = application.get('acronym')
        year = application.get('year')
        if _find_application(acronym, year, attrib.applications):
            return _update_application(global_id, application)
    return _create_application(global_id, application)


def _create_application(global_id, application_to_create):
    attrib = mdl_attribution.attribution_new.find_by_global_id(global_id)
    if not attrib:
        attrib = mdl_attribution.attribution_new.AttributionNew()
    if not attrib.applications:
        attrib.applications = []
    attrib.applications.append(application_to_create)
    attrib.save()
    # Send signal to EPC
    _send_create_application_to_queue(application_to_create)


def _update_application(global_id, application_to_update):
    attrib = mdl_attribution.attribution_new.find_by_global_id(global_id)
    if attrib and attrib.applications:
        acronym = application_to_update.get('acronym')
        year = application_to_update.get('year')
        # Send signal to EPC
        _send_update_application_to_queue(application_to_update)
        # Remove and append new records to json array
        attrib.applications = _delete_application_in_list(acronym, year, attrib.applications)
        attrib.applications.append(application_to_update)
        attrib.save()


def delete_application(global_id, learning_container_year):
    attrib = mdl_attribution.attribution_new.find_by_global_id(global_id)
    if attrib and attrib.applications:
        year = learning_container_year.academic_year.year
        acronym = learning_container_year.acronym
        application_to_delete = _find_application(acronym, year, attrib.applications)
        # Send signal to EPC
        _send_deletion_application_to_queue(application_to_delete)
        # Remove from json array
        attrib.applications = _delete_application_in_list(acronym, year, attrib.applications)
        attrib.save()
        return True
    return False


def _delete_application_in_list(acronym, year, application_list):
    return [application for application in application_list if not (acronym == application.get('acronym') and
                                                                    year == application.get('year'))]


def _find_application(acronym, year, applications_list):
    if applications_list:
        return next((application for application in applications_list
                      if application.get('year') == year and application.get('acronym') == acronym),
                     None)
    return None


def _send_create_application_to_queue(application):
    pass


def _send_deletion_application_to_queue(application):
    DELETE_OPERATION = "delete"
    queue_name = settings.QUEUES.get('QUEUES_NAME', {}).get('ATTRIBUTION')

    if queue_name:
        queue_sender.send_message(queue_name, {
          'operation': DELETE_OPERATION,
          **application
        })


def _send_update_application_to_queue(application):
    pass


def send_mail_applications_summary(global_id):
    application_list = get_application_list(global_id)
    if not application_list:
        return _('no_application_found')
    person = mdl_base.person.find_by_global_id(global_id)

    html_template_ref = 'applications_confirmation_html'
    txt_template_ref = 'applications_confirmation_txt'
    receivers = [message_config.create_receiver(person.id, person.email, person.language)]
    template_base_data = {
        'first_name': person.first_name,
        'last_name': person.last_name,
        'applications': _get_application_list_str(application_list)
    }
    message_content = message_config.create_message_content(html_template_ref, txt_template_ref,
                                                            None, receivers, template_base_data, None)
    return message_service.send_messages(message_content)


def _get_application_list_str(application_list):
    applications_str = ["*\t{}\t{}\t{}".format(application.get('acronym', ''),
                                               application.get(learning_component_year_type.LECTURING, ''),
                                               application.get(learning_component_year_type.PRACTICAL_EXERCISES, ''))
                        for application in application_list ]
    return "\n".join(applications_str)