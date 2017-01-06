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
import datetime

from django.conf import settings
from django.forms import formset_factory
from django.shortcuts import render

from performance import models as mdl_performance
from base import models as mdl_base
from attribution import models as mdl_attribution
from base.models.enums import component_type
from attribution.forms.attribution import AttributionForm
from django.contrib.auth.decorators import login_required
import json
from base.models.enums import component_type
from django.core.serializers.json import DjangoJSONEncoder

CHARGE_NULL = 0

# def generate_message_by_tutor_application_list(tutor_application_list):
#     print(tutor_application_list)
#     message = dict()
#     if tutor_application_list:
#         for a_tutor_application in tutor_application_list:
#             line_attribution = dict()
#             line_attribution['learning_unit_year'] = a_tutor_application.learning_unit_year.id
#             line_attribution['person'] = a_tutor_application.tutor.external_id
#             line_attribution['function'] = a_tutor_application.function
#             line_attribution['remark'] = a_tutor_application.remark
#             line_attribution['course_summary'] = a_tutor_application.course_summary
#
#             application_charges = mdl_attribution.application_charge.search(a_tutor_application, None)
#             for application_charge in application_charges:
#                 if application_charge.learning_unit_component.type == component_type.LECTURING:
#                     line_attribution['lecturing_allocation'] = application_charge.allocation_charge
#                 if application_charge.learning_unit_component.type == component_type.PRACTICAL_EXERCISES:
#                     line_attribution['practical_allocation'] = application_charge.allocation_charge
#
#     return json.dumps(message)


def get_learning_unit_info(a_learning_unit_year_external_id):
    # Example of external_id osis.learning_unit_year_428750_2017
    learning_unit_year_infos = dict()
    if a_learning_unit_year_external_id:
        external_id_array = str(a_learning_unit_year_external_id).split('_')
        learning_unit_year_infos['reference'] = external_id_array[-2]
        learning_unit_year_infos['year'] = external_id_array[-1]
    return learning_unit_year_infos


def get_tutor_info(a_tutor_external_id):
    # Example of external_id osis.osis.tutor_00025561
    if a_tutor_external_id:
        external_id_array = str(a_tutor_external_id).split('_')
        return external_id_array[-1]
    return None


def get_allocation_charge(a_tutor_application, a_component_type):
    a_learning_unit_component = mdl_base.learning_unit_component.find_first(a_tutor_application.learning_unit_year,
                                                                            a_component_type)
    an_application_charge = mdl_attribution.application_charge.find_first(a_tutor_application,
                                                                          a_learning_unit_component)
    if an_application_charge:
        return an_application_charge.allocation_charge
    return CHARGE_NULL


def generate_message_from_application_charge(an_application_charge):
    a_tutor_application = an_application_charge.tutor_application
    line_attribution = dict()
    line_attribution['learning_unit_year'] = get_learning_unit_info(a_tutor_application.learning_unit_year.external_id)
    line_attribution['tutor'] = get_tutor_info(a_tutor_application.tutor.external_id)
    line_attribution['function'] = a_tutor_application.function
    line_attribution['remark'] = a_tutor_application.remark
    line_attribution['course_summary'] = a_tutor_application.course_summary

    if an_application_charge.learning_unit_component.type == component_type.LECTURING:
        line_attribution['lecturing_allocation'] = an_application_charge.allocation_charge
        line_attribution['practical_allocation'] = get_allocation_charge(a_tutor_application,
                                                                         component_type.PRACTICAL_EXERCISES)
    if an_application_charge.learning_unit_component.type == component_type.PRACTICAL_EXERCISES:
        line_attribution['practical_allocation'] = an_application_charge.allocation_charge
        line_attribution['lecturing_allocation'] = get_allocation_charge(a_tutor_application,
                                                                         component_type.LECTURING)
    msg= json.dumps(line_attribution, cls=DjangoJSONEncoder)
    print(msg)
    return msg