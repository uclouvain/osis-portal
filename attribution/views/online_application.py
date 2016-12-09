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
from attribution import models as mdl_attribution
from attribution.views import teaching_load
from base import models as mdl_base
from base.models.enums import component_type
from attribution.models.enums import function


ACRONYM = 'acronym'
TITLE = 'title'
LECTURING_DURATION = 'lecturing_duration'
PRACTICAL_DURATION = 'practice_duration'
START = 'start'
END = 'end'
ATTRIBUTION_CHARGE_LECTURING = 'attribution_charge_lecturing'
ATTRIBUTION_CHARGE_PRACTICAL = 'attribution_charge_practical'
FUNCTION = 'function'

VACANT_ATTRIBUTION_CHARGE_LECTURING = 'vacant_attribution_charge_lecturing'
VACANT_ATTRIBUTION_CHARGE_PRACTICAL = 'vacant_attribution_charge_practical'

TUTOR_APPLICATION = 'tutor_application'
REMARK = 'remark'
COURSE_SUMMARY='course_summary'

TWO_DECIMAL_FORMAT = "%0.2f"

def get_year(a_year):
    if a_year:
        return a_year.year
    return None


def get_attributions_allocated(a_year, a_tutor):

    an_academic_year = mdl_base.academic_year.find_by_year(a_year)
    if a_tutor and an_academic_year:
        return get_attribution_data( mdl_attribution.attribution.find_by_tutor_year_order_by_acronym_fonction(a_tutor, an_academic_year))




def get_attribution_data(attributions):
    attributions_results = []
    for attribution in attributions:
        print(attribution.learning_unit_year.acronym ,attribution.learning_unit_year.academic_year.year, attribution.start_date,   attribution.end_date)
        attributions_results.append(
            get_attribution_informations(attribution.learning_unit_year,
                                         attribution.start_date,
                                         attribution.end_date,
                                         attribution.tutor,
                                         attribution.function))
    return attributions_results


def get_attribution_informations(a_learning_unit_year, a_start_date, an_end_date, a_tutor, a_function):
    return {
        ACRONYM: a_learning_unit_year.acronym,
        TITLE: a_learning_unit_year.title,
        LECTURING_DURATION: format_duration(get_learning_unit_component_duration(a_learning_unit_year, component_type.LECTURING)),
        PRACTICAL_DURATION: format_duration(get_learning_unit_component_duration(a_learning_unit_year, component_type.PRACTICAL_EXERCISES)),
        START: get_year(a_start_date),
        END: get_year(an_end_date),
        ATTRIBUTION_CHARGE_LECTURING:
            format_duration(teaching_load.get_attribution_allocation_charge(a_tutor,
                                                                            a_learning_unit_year,
                                                                            component_type.LECTURING)),
        ATTRIBUTION_CHARGE_PRACTICAL:
            format_duration(teaching_load.get_attribution_allocation_charge(a_tutor,
                                                                            a_learning_unit_year,
                                                                            component_type.PRACTICAL_EXERCISES)),
        FUNCTION: a_function}


def get_application_informations(a_tutor_application):
    a_learning_unit_year = a_tutor_application.learning_unit_year
    a_tutor = a_tutor_application.tutor
    a_function = a_tutor_application.function
    return {
        TUTOR_APPLICATION: a_tutor_application,
        LECTURING_DURATION: format_duration(get_learning_unit_component_duration(a_learning_unit_year, component_type.LECTURING)),
        PRACTICAL_DURATION: format_duration(get_learning_unit_component_duration(a_learning_unit_year, component_type.PRACTICAL_EXERCISES)),
        ATTRIBUTION_CHARGE_LECTURING:
            format_duration(teaching_load.get_attribution_allocation_charge(a_tutor,
                                                                            a_learning_unit_year,
                                                                            component_type.LECTURING)),
        ATTRIBUTION_CHARGE_PRACTICAL:
            format_duration(teaching_load.get_attribution_allocation_charge(a_tutor,
                                                                            a_learning_unit_year,
                                                                            component_type.PRACTICAL_EXERCISES))}


def get_learning_unit_component_duration(a_learning_unit_year, a_component_type):
    a_learning_unit_components = mdl_base.learning_unit_component.search(a_learning_unit_year, a_component_type)
    tot_duration = 0
    for a_learning_unit_component in a_learning_unit_components:
        tot_duration += a_learning_unit_component.duration
    return tot_duration


def format_duration(duration):
    return TWO_DECIMAL_FORMAT % (duration,)


def get_vacant_learning_units(a_year):
    learning_unit_results = []
    an_academic_year = mdl_base.academic_year.find_by_year(a_year)
    learning_units_year = mdl_base.learning_unit_year.search_order_by_acronym(an_academic_year)
    for learning_unit_year in learning_units_year:
        tot_learning_unit_year_duration = teaching_load.sum_learning_unit_year_duration(learning_unit_year)
        tot_attribution_allocated = sum_attribution_allocation_charges(learning_unit_year)
        if tot_learning_unit_year_duration != tot_attribution_allocated:
            learning_unit_results.append({ACRONYM: learning_unit_year.acronym,
                                          TITLE: learning_unit_year.title,
                                          LECTURING_DURATION: format_duration(get_learning_unit_component_duration(learning_unit_year, component_type.LECTURING)),
                                          PRACTICAL_DURATION: format_duration(get_learning_unit_component_duration(learning_unit_year, component_type.PRACTICAL_EXERCISES)),

                                          VACANT_ATTRIBUTION_CHARGE_LECTURING:
                                              format_duration(get_vacant_attribution_allocation_charge(learning_unit_year,
                                                                                                              component_type.LECTURING)),
                                          VACANT_ATTRIBUTION_CHARGE_PRACTICAL:
                                              format_duration(get_vacant_attribution_allocation_charge(learning_unit_year,
                                                                                                              component_type.PRACTICAL_EXERCISES)),
                                          })

    return learning_unit_results


def sum_attribution_allocation_charges(a_learning_unit_year):
    tot = teaching_load.get_attribution_allocation_charge(None, a_learning_unit_year, component_type.LECTURING )
    return tot + teaching_load.get_attribution_allocation_charge(None, a_learning_unit_year, component_type.PRACTICAL_EXERCISES )


def get_vacant_attribution_allocation_charge(a_learning_unit_year, a_component_type):
    return get_learning_unit_component_duration(a_learning_unit_year, a_component_type) - teaching_load.get_attribution_allocation_charge(None, a_learning_unit_year, a_component_type)


def get_applications(a_year, a_tutor):
    application_list = []
    an_academic_year = mdl_base.academic_year.find_by_year(a_year)
    if an_academic_year:
        tutor_applications = mdl_attribution.tutor_application.find_by_dates_tutor(get_start_date(an_academic_year), get_end_date(an_academic_year), a_tutor)
        for tutor_application in tutor_applications:
            application_list.append(get_application_informations(tutor_application))
    return application_list


def define_function(a_learning_unit_year):
    if sum_attribution_allocation_charges(a_learning_unit_year) == teaching_load.sum_learning_unit_year_duration(a_learning_unit_year):
        return function.HOLDER
    return function.CO_HOLDER


def get_start_date(an_academic_year):
    if an_academic_year:
        if an_academic_year.start_date is None:
            return datetime.datetime(an_academic_year.year, 9, 15)
        else:
            return an_academic_year.start_date
    return None



def get_end_date(an_academic_year):
    if an_academic_year:
        if an_academic_year.end_date is None:
            return datetime.datetime(an_academic_year.year+1, 9, 14)
        else:
            return an_academic_year.end_date

    return None


def create_tutor_application(a_learning_unit_year, data):
    attribution_lecturing_duration = data[ATTRIBUTION_CHARGE_LECTURING]
    attribution_practical_duration = data[ATTRIBUTION_CHARGE_PRACTICAL]
    remark = data[REMARK]
    course_summary = data[COURSE_SUMMARY]

    a_new_tutor_application = mdl_attribution.tutor_application.TutorApplication()
    a_new_tutor_application.function = define_function(a_learning_unit_year)
    a_new_tutor_application.learning_unit_year = a_learning_unit_year
    a_new_tutor_application.remark = remark
    a_new_tutor_application.course_summary = course_summary
    a_new_tutor_application.start_date = get_start_date(a_learning_unit_year.academic_year)
    a_new_tutor_application.end_date = get_end_date(a_learning_unit_year.academic_year)
    a_new_tutor_application.save()

    create_application_charge(a_new_tutor_application, attribution_lecturing_duration, component_type.LECTURING)
    create_application_charge(a_new_tutor_application, attribution_practical_duration, component_type.PRACTICAL_EXERCISES)


def create_application_charge(a_new_tutor_application, charge_duration, a_component_type):
    a_learning_unit_component = mdl_base.learning_unit_component.search(a_new_tutor_application.learning_unit_year, a_component_type)
    if a_learning_unit_component:
        a_new_application_charge = mdl_attribution.application_charge.ApplicationCharge(tutor_application=a_new_tutor_application,
                                                                                        learning_unit_component=a_learning_unit_component,
                                                                                        allocation_charge=charge_duration)
        a_new_application_charge.save()


def get_terminating_charges(a_year, a_tutor):
    print('get_terminating_charges')
    an_academic_year = mdl_base.academic_year.find_by_year(a_year)
    for a in mdl_attribution.attribution.search(None,None):
        print(a.end_date)
    print('kkk')
    if an_academic_year:
        attribution_charges = mdl_attribution.attribution.find_by_tutor_dates(a_tutor,
                                                                              get_start_date(an_academic_year),
                                                                              get_end_date(an_academic_year))

        print('nb',len(attribution_charges))
        return get_attribution_data(attribution_charges)
    return []



