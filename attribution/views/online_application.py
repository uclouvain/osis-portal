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
LEARNING_UNIT_YEAR_ID = 'learning_unit_year_id'
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
TEAM = 'team'
START_ACADEMIC_YEAR = 'start_academic_year'
END_ACADEMIC_YEAR = 'end_academic_year'
ALREADY_CANDIDATED = 'already_candidated'
TWO_DECIMAL_FORMAT = "%0.2f"
CHARGE_NUL = 0
ALLOCATION_CHARGE_NUL = 0
YEAR = 2015
YEAR_OVER = 2016
NEXT_YEAR = 2017


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
                                         attribution))
    return attributions_results


def get_attribution_informations(a_learning_unit_year, a_start_date, an_end_date, a_tutor, a_function, an_attribution):
    start = get_year(a_start_date)
    end = get_year(an_end_date)
    d = {ATTRIBUTION_ID: an_attribution.id,
         ACRONYM: a_learning_unit_year.acronym,
         TITLE: a_learning_unit_year.title,
         LECTURING_DURATION: get_learning_unit_component_duration(a_learning_unit_year, component_type.LECTURING),
         PRACTICAL_DURATION: get_learning_unit_component_duration(a_learning_unit_year,
                                                                  component_type.PRACTICAL_EXERCISES),
         START: start,
         END: end,
         ATTRIBUTION_CHARGE_LECTURING:
             teaching_load.attribution_allocation_charge(a_learning_unit_year,
                                                         component_type.LECTURING,
                                                         an_attribution),
         ATTRIBUTION_CHARGE_PRACTICAL:
             teaching_load.attribution_allocation_charge(a_learning_unit_year,
                                                         component_type.PRACTICAL_EXERCISES,
                                                         an_attribution),
         FUNCTION: a_function,
         RENEW: define_renew(a_tutor,
                             a_learning_unit_year),
         TEAM: a_learning_unit_year.team,
         START_ACADEMIC_YEAR:  "{0}-{1}".format(start, start+1),
         END_ACADEMIC_YEAR: "{0}-{1}".format(end-1, end),
         ALREADY_CANDIDATED: define_already_candidated(a_tutor,
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
        LECTURING_DURATION: a_lecturing_duration,
        PRACTICAL_DURATION: a_practical_duration,
        ATTRIBUTION_CHARGE_LECTURING: lecturing_allocated,
        ATTRIBUTION_CHARGE_PRACTICAL: practical_allocated,
        APPLICATION_CHARGE_LECTURING: get_application_charge(a_tutor,
                                                             a_learning_unit_year,
                                                             component_type.LECTURING),
        APPLICATION_CHARGE_PRACTICAL: get_application_charge(a_tutor,
                                                             a_learning_unit_year,
                                                             component_type.PRACTICAL_EXERCISES),
        VACANT_ATTRIBUTION_CHARGE_LECTURING:
            get_vacant_attribution_allocation_charge(a_learning_unit_year, component_type.LECTURING),
        VACANT_ATTRIBUTION_CHARGE_PRACTICAL:
            get_vacant_attribution_allocation_charge(a_learning_unit_year, component_type.PRACTICAL_EXERCISES)}


def get_learning_unit_component_duration(a_learning_unit_year, a_component_type):
    a_learning_unit_components = mdl_base.learning_unit_component.search(a_learning_unit_year, a_component_type)
    tot_duration = 0
    for a_learning_unit_component in a_learning_unit_components:
        tot_duration += a_learning_unit_component.duration
    return tot_duration


def is_learning_unit_vacant(a_learning_unit_year):
    tot_learning_unit_year_duration = teaching_load.sum_learning_unit_year_duration(a_learning_unit_year)
    tot_attribution_allocated = sum_attribution_allocation_charges(a_learning_unit_year)
    if tot_learning_unit_year_duration != tot_attribution_allocated:
        return True
    return False


def get_learning_unit_informations(a_learning_unit_year):
    return {ACRONYM: a_learning_unit_year.acronym,
            TITLE: a_learning_unit_year.title,
            LECTURING_DURATION: get_learning_unit_component_duration(a_learning_unit_year,
                                                                     component_type.LECTURING),
            PRACTICAL_DURATION: get_learning_unit_component_duration(a_learning_unit_year,
                                                                     component_type.PRACTICAL_EXERCISES),

            VACANT_ATTRIBUTION_CHARGE_LECTURING:
                get_vacant_attribution_allocation_charge(a_learning_unit_year, component_type.LECTURING),
            VACANT_ATTRIBUTION_CHARGE_PRACTICAL:
                get_vacant_attribution_allocation_charge(a_learning_unit_year, component_type.PRACTICAL_EXERCISES),
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
    tot2 = tot + teaching_load.get_attribution_allocation_charge(None,
                                                                 a_learning_unit_year,
                                                                 component_type.PRACTICAL_EXERCISES)
    return tot2


def sum_tutor_application_charges(a_learning_unit_year, a_tutor):
    tot = sum_application_allocation_charges(a_tutor, a_learning_unit_year, component_type.LECTURING)
    tot2 = tot + sum_application_allocation_charges(a_tutor, a_learning_unit_year, component_type.PRACTICAL_EXERCISES)
    return tot2


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


def define_tutor_application_function(a_learning_unit_year, request):
    a_tutor = mdl_base.tutor.find_by_user(request.user)
    if sum_tutor_application_charges(a_learning_unit_year, a_tutor) == teaching_load.sum_learning_unit_year_duration(a_learning_unit_year):
        return function.HOLDER

    return function.CO_HOLDER


def define_function(a_learning_unit_year):
    if sum_attribution_allocation_charges(a_learning_unit_year) == teaching_load.sum_learning_unit_year_duration(a_learning_unit_year):
        return function.HOLDER
    return function.CO_HOLDER


def get_start_date(an_academic_year):
    if an_academic_year:
        if an_academic_year.start_date is None:
            return datetime.datetime(an_academic_year.year, 1, 1)
        else:
            return an_academic_year.start_date
    return None


def get_end_date(an_academic_year):
    return datetime.datetime(an_academic_year.year+1, 1, 1)


def create_tutor_application(a_learning_unit_year, data):
    attribution_lecturing_duration = data[ATTRIBUTION_CHARGE_LECTURING]
    attribution_practical_duration = data[ATTRIBUTION_CHARGE_PRACTICAL]
    remark = data[REMARK]
    course_summary = data[COURSE_SUMMARY]

    a_new_tutor_application = mdl_attribution.tutor_application.TutorApplication()
    a_new_tutor_application.function = define_tutor_application_function(a_learning_unit_year)
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
    a_learning_unit_component = mdl_base.learning_unit_component.find_first(a_new_tutor_application.learning_unit_year,
                                                                            a_component_type)

    if a_learning_unit_component:
        a_new_application_charge = mdl_attribution.application_charge.ApplicationCharge(tutor_application=a_new_tutor_application,
                                                                                        learning_unit_component=a_learning_unit_component,
                                                                                        allocation_charge=charge_duration)
        a_new_application_charge.save()


def is_vacant(a_learning_unit):
    if a_learning_unit:
        if teaching_load.sum_learning_unit_year_duration(a_learning_unit) > sum_attribution_allocation_charges(a_learning_unit):
            return True
    return False


def get_learning_unit_for_next_year(a_learning_unit_year):
    next_academic_year = mdl_base.academic_year.find_by_year(a_learning_unit_year.academic_year.year+1)
    return mdl_base.learning_unit_year.find_first(next_academic_year, a_learning_unit_year.learning_unit)


def get_terminating_charges(a_year, a_tutor):
    an_academic_year = mdl_base.academic_year.find_by_year(a_year)

    if an_academic_year:
        attribution_charges = mdl_attribution.attribution.find_by_tutor_end_date(a_tutor,
                                                                                 get_end_date(an_academic_year))
        attributions_vacant = []
        for attribution in attribution_charges:
            attributions_vacant.append(attribution)

        return get_attribution_data(attributions_vacant)
    return []


@login_required
def home(request):
    a_tutor = mdl_base.tutor.find_by_user(request.user)
    attributions = get_attributions_allocated(NEXT_YEAR, a_tutor)
    applications = get_applications(NEXT_YEAR, a_tutor)
    tot_lecturing = 0
    tot_practical = 0
    if attributions:
        for attribution_informations in attributions:
            tot_lecturing = tot_lecturing + attribution_informations[ATTRIBUTION_CHARGE_LECTURING]
            tot_practical = tot_practical + attribution_informations[ATTRIBUTION_CHARGE_PRACTICAL]
    return render(request, "attribution_applications.html", {
        'user': request.user,
        'applications': applications,
        'attributions': attributions,
        'academic_year': "{0}-{1}".format(YEAR+1, YEAR+2),
        'tot_lecturing': tot_lecturing,
        'tot_practical': tot_practical})


def get_application_charge(a_tutor, a_learning_unit_year, a_component_type):
    for an_tutor_application in mdl_attribution.tutor_application.search(a_tutor, a_learning_unit_year):
        a_learning_unit_components = mdl_base.learning_unit_component.search(a_learning_unit_year, a_component_type)
        for a_learning_unit_component in a_learning_unit_components:
            applications_charges = mdl_attribution.application_charge.search(an_tutor_application,
                                                                             a_learning_unit_component)
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

    attributions = get_terminating_charges(YEAR_OVER, a_tutor)
    return render(request, "attribution_application_form.html", {
        'application': None,
        'attributions': attributions})


def search(request):
    learning_unit_acronym = request.GET['learning_unit_acronym']
    a_tutor = mdl_base.tutor.find_by_user(request.user)
    attribution = None
    if learning_unit_acronym and len(learning_unit_acronym.strip()) > 0:
        return render(request, "attribution_vacant.html", {
            'attribution': get_learning_unit_year_vacant(NEXT_YEAR, learning_unit_acronym)})
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


def save_on_new_learning_unit(request):
    new_tutor_application = create_tutor_application_from_user_learning_unit_year(request)
    form = ApplicationForm(data=request.POST)

    if form.is_valid():
        if new_tutor_application:
            new_tutor_application.course_summary = form['course_summary'].value()
            new_tutor_application.remark = form['remark'].value()
            new_tutor_application.save()

        application_charge_create(new_tutor_application,
                                  form['charge_lecturing'].value().replace(',', '.'),
                                  component_type.LECTURING)
        application_charge_create(new_tutor_application,
                                  form['charge_practical'].value().replace(',', '.'),
                                  component_type.PRACTICAL_EXERCISES)

        new_tutor_application.function = define_tutor_application_function(new_tutor_application.learning_unit_year,
                                                                           request)
        new_tutor_application.save()

        return home(request)
    else:
        return render(request, "application_form.html", {
            'application': get_application_informations(new_tutor_application),
            'attributions': get_terminating_charges(YEAR, new_tutor_application.tutor),
            'form': form})


def create_tutor_application_from_user_learning_unit_year(request):
    new_tutor_application = mdl_attribution.tutor_application.TutorApplication()
    new_tutor_application.tutor = mdl_base.tutor.find_by_user(request.user)
    new_tutor_application.learning_unit_year = mdl_base.learning_unit_year.find_by_id(
        request.POST.get('learning_unit_year_id'))
    new_tutor_application.start_date = get_start_date(new_tutor_application.learning_unit_year.academic_year)
    new_tutor_application.end_date = get_end_date(new_tutor_application.learning_unit_year.academic_year)
    return new_tutor_application


def save(request, tutor_application_id):
    tutor_application_to_save = mdl_attribution.tutor_application.find_by_id(tutor_application_id)
    form = ApplicationForm(data=request.POST)

    if form.is_valid():
        allocation_charge_update(request.POST.get('application_charge_lecturing_id'),
                                 form['charge_lecturing'].value().replace(',', '.'))
        allocation_charge_update(request.POST.get('application_charge_practical_id'),
                                 form['charge_practical'].value().replace(',', '.'))

        if tutor_application_to_save:
            tutor_application_to_save.course_summary = form['course_summary'].value()
            tutor_application_to_save.remark = form['remark'].value()
            tutor_application_to_save.function = define_tutor_application_function(tutor_application_to_save.learning_unit_year,
                                                                                   request)
            tutor_application_to_save.save()
        return home(request)
    else:
        return render(request, "application_form.html", {
            'application': get_application_informations(tutor_application_to_save),
            'attributions': get_terminating_charges(YEAR, tutor_application_to_save.tutor),
            'form': form})


def application_charge_create(a_tutor_application, a_charge, a_component_type):
    a_learning_unit_year = a_tutor_application.learning_unit_year
    a_learning_unit_component = mdl_base.learning_unit_component.find_first(a_learning_unit_year, a_component_type)
    if a_tutor_application and a_learning_unit_component and a_learning_unit_year:
        application_charge = mdl_attribution.application_charge\
            .ApplicationCharge(tutor_application=a_tutor_application,
                               learning_unit_component=a_learning_unit_component,
                               allocation_charge=a_charge)
        application_charge.save()


def allocation_charge_update(an_application_charge_id, a_field_value):
    if an_application_charge_id:
        application_charge = mdl_attribution.application_charge.find_by_id(an_application_charge_id)
        if application_charge and a_field_value:
            application_charge.allocation_charge = a_field_value
            application_charge.save()


def get_learning_unit_year_vacant(a_year, an_acronym):
    print('get_learning_unit_year_vacant')
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
        return get_new_attribution_informations(a_learning_unit_year)

    return None


def get_new_attribution_informations(a_learning_unit_year):
    d = {ACRONYM: a_learning_unit_year.acronym,
         TITLE: a_learning_unit_year.title,
         LECTURING_DURATION: get_learning_unit_component_duration(a_learning_unit_year,
                                                                  component_type.LECTURING),
         PRACTICAL_DURATION: get_learning_unit_component_duration(a_learning_unit_year,
                                                                  component_type.PRACTICAL_EXERCISES),

         LEARNING_UNIT_YEAR_ID: a_learning_unit_year.id}
    return d


def define_renew(a_tutor, a_learning_unit_year):
    next_learning_unit_year = get_learning_unit_for_next_year(a_learning_unit_year)
    if is_vacant(next_learning_unit_year):
        tutor_applications = mdl_attribution.tutor_application.search(a_tutor, next_learning_unit_year)
        if tutor_applications:
            return False
        return True

    else:
        return False


def new(request, a_learning_unit_year_id=None):
    learning_unit_year = None
    tutor_application_to_save = None
    if a_learning_unit_year_id:
        learning_unit_year = mdl_base.learning_unit_year.find_by_id(a_learning_unit_year_id)
        tutor_application_to_save = create_tutor_application_from_learning_unit_year(learning_unit_year, request)
    form = ApplicationForm()
    if tutor_application_to_save:
        data = {'charge_lecturing': get_vacant_attribution_allocation_charge(learning_unit_year, component_type.LECTURING),
                'charge_practical': get_vacant_attribution_allocation_charge(learning_unit_year, component_type.PRACTICAL_EXERCISES),
                'remark': None,
                'course_summary': None,
                'max_charge_lecturing': get_learning_unit_component_duration(learning_unit_year, component_type.LECTURING),
                'max_charge_practical': get_learning_unit_component_duration(learning_unit_year, component_type.PRACTICAL_EXERCISES)}
        form = ApplicationForm(initial=data)
    return render(request, "application_form.html", {
        'application': get_application_informations(tutor_application_to_save),
        'form': form})


def create_tutor_application_from_learning_unit_year(learning_unit_year, request):

    a_tutor = mdl_base.tutor.find_by_user(request.user)

    if learning_unit_year:
        attribution_lecturing_duration = teaching_load.get_attribution_allocation_charge(a_tutor,
                                                                                         learning_unit_year,
                                                                                         component_type.LECTURING)
        attribution_practical_duration = teaching_load.get_attribution_allocation_charge(a_tutor,
                                                                                         learning_unit_year,
                                                                                         component_type.PRACTICAL_EXERCISES)
        next_academic_year = mdl_base.academic_year.find_by_year(learning_unit_year.academic_year.year+1)


        next_learning_unit_year = mdl_base.learning_unit_year.find_first(next_academic_year,
                                                                         learning_unit_year.learning_unit)
        a_new_tutor_application = mdl_attribution.tutor_application.TutorApplication()
        a_new_tutor_application.tutor = a_tutor

        a_new_tutor_application.learning_unit_year = learning_unit_year
        a_new_tutor_application.remark = None
        a_new_tutor_application.course_summary = None
        a_new_tutor_application.start_date = get_start_date(learning_unit_year.academic_year)
        a_new_tutor_application.end_date = get_end_date(learning_unit_year.academic_year)

        return a_new_tutor_application
    return None


def sum_application_allocation_charges(a_tutor, a_learning_unit_year, a_component_type):
    tutor_application_list = mdl_attribution.tutor_application.search(a_tutor, a_learning_unit_year)
    tot_charge = ALLOCATION_CHARGE_NUL
    for a_tutor_application in tutor_application_list:
        a_learning_unit_components = mdl_base.learning_unit_component.search(a_learning_unit_year, a_component_type)
        for a_learning_unit_component in a_learning_unit_components:
            attribution_charges = mdl_attribution.application_charge.search(None, a_learning_unit_component)
            for attribution_charge in attribution_charges:
                tot_charge += attribution_charge.allocation_charge

    return tot_charge


def define_already_candidated(a_tutor, a_learning_unit_year):
    next_learning_unit_year = get_learning_unit_for_next_year(a_learning_unit_year)

    tutor_applications = mdl_attribution.tutor_application.search(a_tutor, next_learning_unit_year)
    if tutor_applications:
        return True
    return False
