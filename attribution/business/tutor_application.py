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
import time
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone

from attribution import models as mdl_attribution
from attribution.utils import tutor_application_epc
from base import models as mdl_base
from base.models.enums import learning_component_year_type
from osis_common.messaging import message_config, send_message as message_service


def get_application_list(global_id, academic_year=None):
    """
        Return the list of attribution that a tutor have applied
    """
    if not academic_year:
        academic_year = get_application_year()

    attrib = mdl_attribution.attribution_new.find_by_global_id(global_id)
    if attrib and attrib.applications:
        application_list = list(_filter_by_years(attrib.applications, academic_year.year))
        application_list = _resolve_learning_container_year_info(application_list, academic_year)
        return _order_by_pending_and_acronym(application_list)
    return None


def get_application(global_id, learning_container_year):
    academic_year = learning_container_year.academic_year
    application_list = get_application_list(global_id, academic_year)
    return _find_application(learning_container_year.acronym, academic_year.year, application_list)


def mark_attribution_already_applied(attributions_vacant, global_id, academic_year, applications=None):
    if not applications:
        applications = get_application_list(global_id, academic_year)

    for attribution in attributions_vacant:
        attribution['already_applied'] = next((True for application in applications if
                                               application.get('acronym') == attribution.get('acronym')), False) \
                                          if applications else False
    return attributions_vacant


def get_application_year():
    # Application year is always for next year
    return mdl_base.academic_year.find_next_academic_year()


def create_or_update_application(global_id, application):
    attrib = mdl_attribution.attribution_new.find_by_global_id(global_id)
    if attrib:
        acronym = application.get('acronym')
        year = application.get('year')
        application_found = _find_application(acronym, year, attrib.applications)
        if application_found:
            if can_be_updated(application_found):
                return _update_application(global_id, application)
            else:
                raise ValueError("applications_in_pending_state")
    return _create_application(global_id, application)


def set_pending_flag(global_id, application, flag=None):
    if can_be_updated(application):
        application['pending'] = flag
        return _update_application(global_id, application)
    else:
        raise ValueError("applications_in_pending_state")


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
            application[l_component_year.type] = l_component_year.volume_declared_vacant
    return application_list


def _create_application(global_id, application_to_create):
    attrib = mdl_attribution.attribution_new.find_by_global_id(global_id)
    if not attrib:
        attrib = mdl_attribution.attribution_new.AttributionNew(global_id=global_id)
    if not attrib.applications:
        attrib.applications = []
    application_to_create['updated_at'] = _get_unix_time()
    attrib.applications.append(application_to_create)
    return attrib.save()


def can_be_updated(application):
    return application.get('pending') not in [tutor_application_epc.DELETE_OPERATION,
                                              tutor_application_epc.UPDATE_OPERATION]


def _update_application(global_id, application_to_update):
    attrib = mdl_attribution.attribution_new.find_by_global_id(global_id)
    if attrib and attrib.applications:
        acronym = application_to_update.get('acronym')
        year = application_to_update.get('year')
        # Remove and append new records to json array
        attrib.applications = _delete_application_in_list(acronym, year, attrib.applications)
        application_to_update['updated_at'] = _get_unix_time()
        attrib.applications.append(application_to_update)
        return attrib.save()
    return None


def _delete_application_in_list(acronym, year, application_list):
    return [application for application in application_list if
            not (acronym == application.get('acronym') and year == application.get('year'))]


def _find_application(acronym, year, applications_list):
    if applications_list:
        return next((application for application in applications_list
                      if application.get('year') == year and application.get('acronym') == acronym),
                     None)
    return None


def _get_application_list_str(application_list):
    applications_str = ["*\t{}\t{}\t{}".format(application.get('acronym', ''),
                                               application.get(learning_component_year_type.LECTURING, ''),
                                               application.get(learning_component_year_type.PRACTICAL_EXERCISES, ''))
                        for application in application_list ]
    return "\n".join(applications_str)


def _filter_by_years(attribution_list, year):
    for attribution in attribution_list:
        if attribution.get('year') == year:
            yield attribution


def _filter_pending_delete(attribution_list):
    for attribution in attribution_list:
        if attribution.get('pending') != tutor_application_epc.DELETE_OPERATION:
            yield attribution


def _get_unix_time():
    now = timezone.now()
    return time.mktime(now.timetuple())


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