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
from django.utils.translation import ugettext_lazy as _, pgettext_lazy
from attribution import models as mdl_attribution
from attribution.calendar.application_courses_calendar import ApplicationCoursesRemoteCalendar
from attribution.utils import tutor_application_epc
from base import models as mdl_base
from base.models.academic_year import AcademicYear
from base.models.enums import learning_unit_year_subtypes
from osis_common.messaging import message_config, send_message as message_service


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


def get_application(global_id, learning_container_year):
    academic_year = learning_container_year.academic_year
    application_list = get_application_list(global_id, academic_year)
    return _find_application(learning_container_year.acronym, academic_year.year, application_list)


def mark_attribution_already_applied(attributions_vacant, global_id, application_academic_year):
    applications = get_application_list(global_id, application_academic_year)

    for attribution in attributions_vacant:
        already_applied = next((True for application in applications if
                                application.get('acronym') == attribution.get('acronym')), False) \
            if applications else False

        attribution['already_applied'] = already_applied
    return attributions_vacant


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
                raise ValueError(_("Applications in pending state"))
    return _create_application(global_id, application)


def set_pending_flag(global_id, application, flag=None):
    if can_be_updated(application):
        application['pending'] = flag
        return _update_application(global_id, application)
    else:
        raise ValueError(_("Applications in pending state"))


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
    application_courses_years_opened = ApplicationCoursesRemoteCalendar().get_target_years_opened()
    application_academic_year = AcademicYear.objects.get(year=application_courses_years_opened[0])

    application_list = get_application_list(global_id, application_academic_year)
    if not application_list:
        return _('No application found')
    person = mdl_base.person.find_by_global_id(global_id)

    html_template_ref = 'applications_confirmation_html'
    txt_template_ref = 'applications_confirmation_txt'
    receivers = [message_config.create_receiver(person.id, person.email, person.language)]
    applications = _get_applications_table(application_list)
    table_applications = message_config.create_table('applications',
                                                     [pgettext_lazy("applications", "Code"), 'Vol. 1', 'Vol. 2'],
                                                     applications)
    template_base_data = {
        'first_name': person.first_name,
        'last_name': person.last_name,

    }
    message_content = message_config.create_message_content(html_template_ref, txt_template_ref,
                                                            [table_applications], receivers, template_base_data, None)
    return message_service.send_messages(message_content)


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


def _create_application(global_id, application_to_create):
    attrib = mdl_attribution.attribution_new.find_by_global_id(global_id)
    if not attrib:
        attrib = mdl_attribution.attribution_new.AttributionNew(global_id=global_id)
    if not attrib.applications:
        attrib.applications = []
    application_to_create['updated_at'] = _get_serialized_time()
    attrib.applications.append(application_to_create)
    return attrib.save()


def can_be_updated(application):
    return application.get('pending') not in [tutor_application_epc.DELETE_OPERATION,
                                              tutor_application_epc.UPDATE_OPERATION]


def _update_application(global_id, application_to_update):
    attrib_qs = mdl_attribution.attribution_new.AttributionNew.objects.select_for_update().filter(
        global_id=global_id,
    ).exclude(
        applications=[]
    )
    with transaction.atomic():
        attrib = attrib_qs.first()
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


def _get_applications_table(application_list):
    applications = []
    for application in application_list:
        applications.append(
            (application.get('acronym', ''),
             application.get('charge_lecturing_asked', ''),
             application.get('charge_practical_asked', ''))
        )
    return applications


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
