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
from django.shortcuts import render
from attribution import models as mdl_attribution
from attribution.views import teaching_load
from base import models as mdl_base
from base.models.enums import component_type
from attribution.models.enums import function
from django.contrib.auth.decorators import login_required
from attribution.forms.application import ApplicationForm

ATTRIBUTION_ID_NAME = 'attribution_id_'

ATTRIBUTION_ID = 'attribution_id'
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

APPLICATION_CHARGE_LECTURING = 'application_charge_lecturing'
APPLICATION_CHARGE_PRACTICAL = 'application_charge_practical'

RENEW = "renew"
TUTOR_APPLICATION = 'tutor_application'
REMARK = 'remark'
COURSE_SUMMARY = 'course_summary'

TWO_DECIMAL_FORMAT = "%0.2f"
CHARGE_NUL = 0

YEAR = datetime.datetime.now().year


def get_year(a_year):
    if a_year:
        return a_year.year
    return None


def get_attributions_allocated(a_year, a_tutor):
    an_academic_year = mdl_base.academic_year.find_by_year(a_year)
    if a_tutor and an_academic_year:
        return get_attribution_data(mdl_attribution.attribution
                                    .find_by_tutor_year_order_by_acronym_fonction(a_tutor, an_academic_year))


def get_attribution_data(attributions):
    attributions_results = []
    for attribution in attributions:
        attributions_results.append(
            get_attribution_informations(attribution.learning_unit_year,
                                         attribution.start_date,
                                         attribution.end_date,
                                         attribution.tutor,
                                         attribution.function,
                                         attribution.id))
    return attributions_results


def get_attribution_informations(a_learning_unit_year, a_start_date, an_end_date, a_tutor, a_function, an_attribution_id):

    d = {ATTRIBUTION_ID: an_attribution_id,
         ACRONYM: a_learning_unit_year.acronym,
         TITLE: a_learning_unit_year.title,
         LECTURING_DURATION: format_duration(get_learning_unit_component_duration(a_learning_unit_year,
                                                                                  component_type.LECTURING)),
         PRACTICAL_DURATION: format_duration(get_learning_unit_component_duration(a_learning_unit_year,
                                                                                  component_type.PRACTICAL_EXERCISES)),
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
        FUNCTION: a_function,
        RENEW: define_renew(a_tutor,
                            a_learning_unit_year)}

    return d


def get_application_informations(a_tutor_application):
    a_learning_unit_year = a_tutor_application.learning_unit_year
    a_tutor = a_tutor_application.tutor
    a_lecturing_duration = get_learning_unit_component_duration(a_learning_unit_year,
                                                                component_type.LECTURING)
    a_practical_duration = get_learning_unit_component_duration(a_learning_unit_year,
                                                                component_type.PRACTICAL_EXERCISES)
    lecturing_allocated = teaching_load.get_attribution_allocation_charge(a_tutor,
                                                                          a_learning_unit_year,
                                                                          component_type.LECTURING)
    practical_allocated = teaching_load.get_attribution_allocation_charge(a_tutor,
                                                                           a_learning_unit_year,
                                                                           component_type.PRACTICAL_EXERCISES)
    return {
        TUTOR_APPLICATION: a_tutor_application,
        LECTURING_DURATION: format_duration(a_lecturing_duration),
        PRACTICAL_DURATION: format_duration(a_practical_duration),
        ATTRIBUTION_CHARGE_LECTURING:
            format_duration(lecturing_allocated),
        ATTRIBUTION_CHARGE_PRACTICAL:
            format_duration(practical_allocated),
        APPLICATION_CHARGE_LECTURING: get_application_charge(a_tutor,
                                                             a_learning_unit_year,
                                                             component_type.LECTURING),
        APPLICATION_CHARGE_PRACTICAL: get_application_charge(a_tutor,
                                                             a_learning_unit_year,
                                                             component_type.PRACTICAL_EXERCISES),
        VACANT_ATTRIBUTION_CHARGE_LECTURING:
            format_duration(get_vacant_attribution_allocation_charge(a_learning_unit_year,
                                                                     component_type.LECTURING)),
        VACANT_ATTRIBUTION_CHARGE_PRACTICAL:
            format_duration(get_vacant_attribution_allocation_charge(a_learning_unit_year,
                                                                     component_type.PRACTICAL_EXERCISES)), }


def get_learning_unit_component_duration(a_learning_unit_year, a_component_type):
    a_learning_unit_components = mdl_base.learning_unit_component.search(a_learning_unit_year, a_component_type)
    tot_duration = 0
    for a_learning_unit_component in a_learning_unit_components:
        tot_duration += a_learning_unit_component.duration
    return tot_duration


def format_duration(duration):
    return TWO_DECIMAL_FORMAT % (duration,)


def is_learning_unit_vacant(a_learning_unit_year):
    tot_learning_unit_year_duration = teaching_load.sum_learning_unit_year_duration(a_learning_unit_year)
    tot_attribution_allocated = sum_attribution_allocation_charges(a_learning_unit_year)
    if tot_learning_unit_year_duration != tot_attribution_allocated:
        return True
    return False


def get_learning_unit_informations(a_learning_unit_year):
    return {ACRONYM: a_learning_unit_year.acronym,
            TITLE: a_learning_unit_year.title,
            LECTURING_DURATION: format_duration(get_learning_unit_component_duration(a_learning_unit_year,
                                                                                     component_type.LECTURING)),
            PRACTICAL_DURATION: format_duration(get_learning_unit_component_duration(a_learning_unit_year,
                                                                                     component_type.PRACTICAL_EXERCISES)),

            VACANT_ATTRIBUTION_CHARGE_LECTURING:
                format_duration(get_vacant_attribution_allocation_charge(a_learning_unit_year,
                                                                         component_type.LECTURING)),
            VACANT_ATTRIBUTION_CHARGE_PRACTICAL:
                format_duration(get_vacant_attribution_allocation_charge(a_learning_unit_year,
                                                                         component_type.PRACTICAL_EXERCISES)),
            }


def get_vacant_learning_units(a_year):
    learning_unit_results = []
    an_academic_year = mdl_base.academic_year.find_by_year(a_year)
    learning_units_year = mdl_base.learning_unit_year.search_order_by_acronym(an_academic_year)
    for learning_unit_year in learning_units_year:
        if is_learning_unit_vacant(learning_unit_year):
            learning_unit_results.append(get_learning_unit_informations(learning_unit_year))

    return learning_unit_results


def sum_attribution_allocation_charges(a_learning_unit_year):
    tot = teaching_load.get_attribution_allocation_charge(None, a_learning_unit_year, component_type.LECTURING)
    return tot + teaching_load.get_attribution_allocation_charge(None, a_learning_unit_year,
                                                                 component_type.PRACTICAL_EXERCISES)


def get_vacant_attribution_allocation_charge(a_learning_unit_year, a_component_type):
    return get_learning_unit_component_duration(a_learning_unit_year, a_component_type) - teaching_load.get_attribution_allocation_charge(None, a_learning_unit_year, a_component_type)


def get_applications(a_year, a_tutor):
    application_list = []
    an_academic_year = mdl_base.academic_year.find_by_year(a_year)
    if an_academic_year:
        tutor_applications = mdl_attribution.tutor_application\
            .find_by_dates_tutor(get_start_date(an_academic_year), get_end_date(an_academic_year), a_tutor)
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

    create_application_charge(a_new_tutor_application, attribution_lecturing_duration,
                              component_type.LECTURING)
    create_application_charge(a_new_tutor_application, attribution_practical_duration,
                              component_type.PRACTICAL_EXERCISES)


def create_application_charge(a_new_tutor_application, charge_duration, a_component_type):
    a_learning_unit_components = mdl_base.learning_unit_component.search(a_new_tutor_application.learning_unit_year,
                                                                         a_component_type)

    if a_learning_unit_components:
        a_new_application_charge = mdl_attribution.application_charge.ApplicationCharge(tutor_application=a_new_tutor_application,
                                                                                        learning_unit_component=a_learning_unit_components[0],
                                                                                        allocation_charge=charge_duration)
        a_new_application_charge.save()


def get_terminating_charges(a_year, a_tutor):
    an_academic_year = mdl_base.academic_year.find_by_year(a_year)
    if an_academic_year:
        attribution_charges = mdl_attribution.attribution.find_by_tutor_dates(a_tutor,
                                                                              get_start_date(an_academic_year),
                                                                              get_end_date(an_academic_year))
        return get_attribution_data(attribution_charges)
    return []


@login_required
def home(request):
    a_tutor = mdl_base.tutor.find_by_user(request.user)
    attributions = get_attributions_allocated(YEAR+1, a_tutor)
    applications = get_applications(YEAR+1, a_tutor)

    return render(request, "attribution_applications.html", {
        'user': request.user,
        'applications': applications,
        'attributions': attributions,
        'academic_year': "{0}-{1}".format(YEAR+1, YEAR+2)})


def get_application_charge(a_tutor, a_learning_unit_year, a_component_type):
    for an_tutor_application in mdl_attribution.tutor_application.search(a_tutor, a_learning_unit_year):
        a_learning_unit_components = mdl_base.learning_unit_component.search(a_learning_unit_year, a_component_type)
        for a_learning_unit_component in a_learning_unit_components:
            applications_charges = mdl_attribution.application_charge.search(an_tutor_application, a_learning_unit_component)
            for application_charge in applications_charges:
                return application_charge

    return None


def delete(request, tutor_application_id):
    tutor_application_to_delete = mdl_attribution.tutor_application.find_by_id(tutor_application_id)
    if tutor_application_to_delete:
        tutor_application_to_delete.delete()
    return home(request)


def attribution_application_form(request):
    a_tutor = mdl_base.tutor.find_by_user(request.user)
    attributions = get_terminating_charges(YEAR, a_tutor)
    return render(request, "attribution_application_form.html", {
        'application': None,
        'attributions': attributions})


def search(request):
    learning_unit_acronym = request.GET['learning_unit_acronym']
    a_tutor = mdl_base.tutor.find_by_user(request.user)
    if learning_unit_acronym and len(learning_unit_acronym.strip()) > 0:
        attributions = get_learning_unit_year_vacant(YEAR+1, learning_unit_acronym)
    else:
        attributions = get_terminating_charges(YEAR, a_tutor)
    return render(request, "attribution_application_form.html", {
        'application': None,
        'attributions': attributions})


def renew(request):
    for key, value in request.POST.items():
        if key.startswith(ATTRIBUTION_ID_NAME):
            attribution_id = int(key.replace(ATTRIBUTION_ID_NAME, ''))
            an_attribution_to_renew = mdl_attribution.attribution.find_by_id(int(attribution_id))
            if an_attribution_to_renew:
                create_tutor_application_from_attribution(an_attribution_to_renew)

    return home(request)


def create_tutor_application_from_attribution(an_attribution):
    attribution_lecturing_duration = teaching_load.get_attribution_allocation_charge(an_attribution.tutor,
                                                                                     an_attribution.learning_unit_year,
                                                                                     component_type.LECTURING)
    attribution_practical_duration = teaching_load.get_attribution_allocation_charge(an_attribution.tutor,
                                                                                     an_attribution.learning_unit_year,
                                                                                     component_type.PRACTICAL_EXERCISES)
    next_academic_year = mdl_base.academic_year.find_by_year(an_attribution.learning_unit_year.academic_year.year+1)

    next_learning_unit_years = mdl_base.learning_unit_year.search(next_academic_year,
                                                                  None,
                                                                  an_attribution.learning_unit_year.learning_unit,
                                                                  None)
    next_learning_unit_year = None
    if next_learning_unit_years:
        next_learning_unit_year = next_learning_unit_years[0]
    a_new_tutor_application = mdl_attribution.tutor_application.TutorApplication()
    a_new_tutor_application.tutor = an_attribution.tutor
    a_new_tutor_application.function = an_attribution.function
    a_new_tutor_application.learning_unit_year = next_learning_unit_year
    a_new_tutor_application.remark = None
    a_new_tutor_application.course_summary = None
    a_new_tutor_application.start_date = get_start_date(next_learning_unit_year.academic_year)
    a_new_tutor_application.end_date = get_end_date(next_learning_unit_year.academic_year)
    a_new_tutor_application.save()

    create_application_charge(a_new_tutor_application,
                              attribution_lecturing_duration,
                              component_type.LECTURING)
    create_application_charge(a_new_tutor_application,
                              attribution_practical_duration,
                              component_type.PRACTICAL_EXERCISES)
    return a_new_tutor_application


def edit(request, tutor_application_id):
    tutor_application_to_update = mdl_attribution.tutor_application.find_by_id(tutor_application_id)
    a_tutor = mdl_base.tutor.find_by_user(request.user)
    attributions = get_terminating_charges(YEAR, a_tutor)

    application = get_application_informations(tutor_application_to_update)
    if application:
        data = {'charge_lecturing': application[APPLICATION_CHARGE_LECTURING].allocation_charge,
                'charge_practical': application[APPLICATION_CHARGE_PRACTICAL].allocation_charge,
                'remark': application[TUTOR_APPLICATION].remark,
                'course_summary': application[TUTOR_APPLICATION].course_summary,
                'max_charge_lecturing': application[VACANT_ATTRIBUTION_CHARGE_LECTURING],
                'max_charge_practical': application[VACANT_ATTRIBUTION_CHARGE_PRACTICAL]}
        form = ApplicationForm(initial=data)
    else:
        form = ApplicationForm()
    return render(request, "application_form.html", {
        'application': application,
        'attributions': attributions,
        'form': form})


def save(request, tutor_application_id):
    tutor_application_to_save = mdl_attribution.tutor_application.find_by_id(tutor_application_id)
    form = ApplicationForm(data=request.POST)

    if form.is_valid():
        allocation_charge_update(request.POST.get('application_charge_lecturing_id'),
                                 form['charge_lecturing'].value())
        allocation_charge_update(request.POST.get('application_charge_practical_id'),
                                 form['charge_practical'].value())

        if tutor_application_to_save:
            tutor_application_to_save.course_summary = form['course_summary'].value()
            tutor_application_to_save.remark = form['remark'].value()
            tutor_application_to_save.function = define_function(tutor_application_to_save.learning_unit_year)
            tutor_application_to_save.save()

        return home(request)

    else:
        attributions = get_terminating_charges(YEAR, tutor_application_to_save.tutor)
        return render(request, "attribution_application_form.html", {
            'application': get_application_informations(tutor_application_to_save),
            'attributions': attributions,
            'form': form})


def allocation_charge_update(an_application_charge_id, a_field_value):
    if an_application_charge_id:
        application_charge = mdl_attribution.application_charge.find_by_id(an_application_charge_id)
        if application_charge and a_field_value:
            application_charge.allocation_charge = a_field_value
            application_charge.save()


def get_learning_unit_year_vacant(a_year, an_acronym):
    an_academic_year = mdl_base.academic_year.find_by_year(a_year)
    learning_unit_years = mdl_base.learning_unit_year.search(an_academic_year, an_acronym, None, None)
    vacant_learning_units = []
    attribution_charges = []
    new_attribution_charges = []
    for a_learning_unit_year in learning_unit_years:
        attributions = mdl_attribution.attribution.search(None, a_learning_unit_year)
        if attributions.exists():
            lecturing_charge_vacant = get_vacant_attribution_allocation_charge(a_learning_unit_year,
                                                                               component_type.LECTURING)
            practical_charge_vacant = get_vacant_attribution_allocation_charge(a_learning_unit_year,
                                                                               component_type.PRACTICAL_EXERCISES)
            if lecturing_charge_vacant > 0 or practical_charge_vacant > 0:
                vacant_learning_units.append(a_learning_unit_year)
                attribution_charges.append(attributions[0])
        else:
            vacant_learning_units.append(a_learning_unit_year)
            new_attribution_charges.append(a_learning_unit_year)

    attributions = get_attribution_data(attribution_charges)
    for a_learning_unit_year in new_attribution_charges:
        attributions.append(get_new_attribution_informations(a_learning_unit_year))

    return attributions


def get_new_attribution_informations(a_learning_unit_year):
    d = {ACRONYM: a_learning_unit_year.acronym,
         TITLE: a_learning_unit_year.title,
         LECTURING_DURATION: format_duration(get_learning_unit_component_duration(a_learning_unit_year,
                                                                                  component_type.LECTURING)),
         PRACTICAL_DURATION: format_duration(get_learning_unit_component_duration(a_learning_unit_year,
                                                                                  component_type.PRACTICAL_EXERCISES))}
    return d


def define_renew(a_tutor, a_learning_unit_year):
    next_academic_year = mdl_base.academic_year.find_by_year(a_learning_unit_year.academic_year.year + 1)
    if next_academic_year and a_learning_unit_year.learning_unit:
        next_learning_unit_years = mdl_base.learning_unit_year.search(next_academic_year,
                                                                      None,
                                                                      a_learning_unit_year.learning_unit,
                                                                      None)
        if next_learning_unit_years.exists():
            tutor_applications = mdl_attribution.tutor_application.search(a_tutor, next_learning_unit_years[0])
            if tutor_applications:
                return False

    else:
        return False
    return True
