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
from attribution.views import tutor_charge
from base import models as mdl_base
from base.models.enums import component_type
from attribution.models.enums import function
from django.contrib.auth.decorators import login_required
from attribution.forms.application import ApplicationForm
from django.conf import settings


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
APPLICATION_POSSIBLE = 'application_possible'
TEAM_APPLICATION_POSSIBLE = 'team_application_possible'
TUTOR_APPLICATION = "tutor_application"

RENEW = "renew"
TEAM = 'team'
START_ACADEMIC_YEAR = 'start_academic_year'
END_ACADEMIC_YEAR = 'end_academic_year'
CHARGE_NUL = 0

APPLICATION_YEAR = settings.APPLICATION_YEAR
YEAR_OVER = APPLICATION_YEAR-1

def get_year(a_year):
    if a_year:
        return a_year.year
    return None


def get_attributions_allocated(a_year, a_tutor):
    an_academic_year = mdl_base.academic_year.find_by_year(a_year)
    if a_tutor and an_academic_year:
        return get_attribution_data(mdl_attribution.attribution
                                    .find_by_tutor_year_order_by_acronym_function(a_tutor, an_academic_year))


def get_attribution_data(attributions):
    attributions_results = []
    for attribution in attributions:
        attributions_results.append(
            get_attribution_informations(attribution))
    return attributions_results


def get_attribution_informations(an_attribution):
    a_learning_unit_year= an_attribution.learning_unit_year
    a_tutor = an_attribution.tutor

    start = get_year(an_attribution.start_date)
    end = get_year(an_attribution.end_date)
    next_learning_unit_year = None
    next_academic_year = mdl_base.academic_year.find_by_year(a_learning_unit_year.academic_year.year+1)
    if next_academic_year:
        next_learning_unit_year = mdl_base.learning_unit_year.find_first(next_academic_year,
                                                                         a_learning_unit_year.learning_unit)

    return {ATTRIBUTION_ID: an_attribution.id,
            ACRONYM: a_learning_unit_year.acronym,
            TITLE: a_learning_unit_year.title,
            LECTURING_DURATION: get_learning_unit_component_duration(a_learning_unit_year, component_type.LECTURING),
            PRACTICAL_DURATION: get_learning_unit_component_duration(a_learning_unit_year,
                                                                     component_type.PRACTICAL_EXERCISES),
            START: start,
            END: end,
            ATTRIBUTION_CHARGE_LECTURING:
                tutor_charge.attribution_allocation_charge(a_learning_unit_year,
                                                            component_type.LECTURING,
                                                            an_attribution),
            ATTRIBUTION_CHARGE_PRACTICAL:
                tutor_charge.attribution_allocation_charge(a_learning_unit_year,
                                                            component_type.PRACTICAL_EXERCISES,
                                                            an_attribution),
            FUNCTION: an_attribution.function,
            RENEW: define_renew_possible(a_tutor, a_learning_unit_year),
            TEAM: a_learning_unit_year.team,
            START_ACADEMIC_YEAR:  "{0}-{1}".format(start, start+1),
            END_ACADEMIC_YEAR: "{0}-{1}".format(end-1, end),
            VACANT_ATTRIBUTION_CHARGE_LECTURING:
                get_vacant_attribution_allocation_charge(next_learning_unit_year, component_type.LECTURING),
            VACANT_ATTRIBUTION_CHARGE_PRACTICAL:
                get_vacant_attribution_allocation_charge(next_learning_unit_year, component_type.PRACTICAL_EXERCISES),
            TUTOR_APPLICATION: get_first_application_tutor(a_tutor, a_learning_unit_year)}


def get_application_informations(a_tutor_application):
    a_learning_unit_year = a_tutor_application.learning_unit_year
    a_tutor = a_tutor_application.tutor
    a_lecturing_duration = get_learning_unit_component_duration(a_learning_unit_year,
                                                                component_type.LECTURING)
    a_practical_duration = get_learning_unit_component_duration(a_learning_unit_year,
                                                                component_type.PRACTICAL_EXERCISES)
    lecturing_allocated = tutor_charge.get_attribution_allocation_charge(a_tutor,
                                                                          a_learning_unit_year,
                                                                          component_type.LECTURING)
    practical_allocated = tutor_charge.get_attribution_allocation_charge(a_tutor,
                                                                          a_learning_unit_year,
                                                                          component_type.PRACTICAL_EXERCISES)
    return {
        TUTOR_APPLICATION: a_tutor_application,
        LECTURING_DURATION: a_lecturing_duration,
        PRACTICAL_DURATION: a_practical_duration,
        ATTRIBUTION_CHARGE_LECTURING: lecturing_allocated,
        ATTRIBUTION_CHARGE_PRACTICAL: practical_allocated,
        APPLICATION_CHARGE_LECTURING: get_tutor_application_charge(component_type.LECTURING, a_tutor_application),
        APPLICATION_CHARGE_PRACTICAL: get_tutor_application_charge(component_type.PRACTICAL_EXERCISES, a_tutor_application),
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
    tot_learning_unit_year_duration = tutor_charge.sum_learning_unit_year_duration(a_learning_unit_year)
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
    return tutor_charge.get_attribution_allocation_charge(None, a_learning_unit_year, component_type.LECTURING) \
           + tutor_charge.get_attribution_allocation_charge(None, a_learning_unit_year, component_type.PRACTICAL_EXERCISES)


def sum_tutor_application_allocated_charges(a_tutor_application):
    return sum_application_charge_allocation_by_component(a_tutor_application, component_type.LECTURING) \
           + sum_application_charge_allocation_by_component(a_tutor_application, component_type.PRACTICAL_EXERCISES)


def get_vacant_attribution_allocation_charge(a_learning_unit_year, a_component_type):
    if a_learning_unit_year:
        return get_learning_unit_component_duration(a_learning_unit_year, a_component_type) - tutor_charge.get_attribution_allocation_charge(None, a_learning_unit_year, a_component_type)
    return CHARGE_NUL


def get_tutor_applications(a_year, a_tutor):
    application_list = []
    an_academic_year = mdl_base.academic_year.find_by_year(a_year)
    if an_academic_year:
        tutor_applications = mdl_attribution.tutor_application\
            .find_by_dates_tutor(get_start_date(an_academic_year), get_end_date(an_academic_year), a_tutor)
        for tutor_application in tutor_applications:
            application_list.append(get_application_informations(tutor_application))
    return application_list


def define_tutor_application_function(a_tutor_application, request):
    a_learning_unit_year = a_tutor_application.learning_unit_year
    if sum_tutor_application_allocated_charges(a_tutor_application) == tutor_charge.sum_learning_unit_year_duration(a_learning_unit_year):
        return function.HOLDER

    return function.CO_HOLDER


def define_function(a_learning_unit_year):
    if sum_attribution_allocation_charges(a_learning_unit_year) == tutor_charge.sum_learning_unit_year_duration(a_learning_unit_year):
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


def create_application_charge(a_new_tutor_application, charge_duration, a_component_type):
    a_learning_unit_component = mdl_base.learning_unit_component.find_first(a_new_tutor_application.learning_unit_year,
                                                                            a_component_type)

    if a_learning_unit_component:
        a_new_application_charge = mdl_attribution.application_charge.\
            ApplicationCharge(tutor_application=a_new_tutor_application,
                              learning_unit_component=a_learning_unit_component,
                              allocation_charge=charge_duration)
        a_new_application_charge.save()


def is_vacant(a_learning_unit_year):
    if a_learning_unit_year:
        return a_learning_unit_year.vacant
    return False


def get_learning_unit_for_next_year(a_learning_unit_year):
    return mdl_base.learning_unit_year\
        .find_first(mdl_base.academic_year.find_by_year(a_learning_unit_year.academic_year.year+1),
                    a_learning_unit_year.learning_unit)


def get_terminating_charges(a_year, a_tutor):
    an_academic_year = mdl_base.academic_year.find_by_year(a_year)

    if an_academic_year:
        attribution_charges = mdl_attribution.attribution.find_by_tutor_end_date(a_tutor,
                                                                                 get_end_date(an_academic_year))
        attributions_vacant = []
        for attribution in attribution_charges:
            next_learning_unit_year = get_learning_unit_for_next_year(attribution.learning_unit_year)
            if not existing_tutor_application_for_next_year(a_tutor, attribution.learning_unit_year):
                if next_learning_unit_year.in_charge and attribution.function != function.DEPUTY:
                    attributions_vacant.append(attribution)
        return get_attribution_data(attributions_vacant)
    return []


@login_required
def home(request):
    a_tutor = mdl_base.tutor.find_by_user(request.user)
    attributions = get_attributions_allocated(APPLICATION_YEAR, a_tutor)
    tot_lecturing = 0
    tot_practical = 0
    if attributions:
        for attribution_informations in attributions:
            tot_lecturing = tot_lecturing + attribution_informations[ATTRIBUTION_CHARGE_LECTURING]
            tot_practical = tot_practical + attribution_informations[ATTRIBUTION_CHARGE_PRACTICAL]
    return render(request, "attribution_applications.html", {
        'user': request.user,
        'applications': get_tutor_applications(APPLICATION_YEAR, a_tutor),
        'attributions': attributions,
        'academic_year': "{0}-{1}".format(APPLICATION_YEAR, APPLICATION_YEAR+1),
        'tot_lecturing': tot_lecturing,
        'tot_practical': tot_practical})


def get_tutor_application_charge(a_component_type, a_tutor_application):
    a_learning_unit_component = mdl_base.learning_unit_component.find_first(a_tutor_application.learning_unit_year, a_component_type)

    return mdl_attribution.application_charge.find_first(a_tutor_application, a_learning_unit_component)


def get_application_charge(a_tutor, a_learning_unit_year, a_component_type):
    print('get_application_charge')
    for an_tutor_application in mdl_attribution.tutor_application.search(a_tutor, a_learning_unit_year):
        for a_learning_unit_component in mdl_base.learning_unit_component.search(a_learning_unit_year, a_component_type):
            application_charges = mdl_attribution.application_charge.search(an_tutor_application,
                                                                            a_learning_unit_component)
            for application_charge in application_charges:
                print('before return', len(application_charges))
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
        'attributions': attributions,
        'application_academic_year': "{0}-{1}".format(APPLICATION_YEAR, APPLICATION_YEAR + 1),
        'over_academic_year': "{0}-{1}".format(YEAR_OVER, YEAR_OVER + 1)})


def search(request):
    learning_unit_acronym = request.GET['learning_unit_acronym']
    a_tutor = mdl_base.tutor.find_by_user(request.user)

    if learning_unit_acronym and len(learning_unit_acronym.strip()) > 0:
        return render(request, "attribution_vacant.html", {
            'attribution': get_learning_unit_year_vacant(APPLICATION_YEAR, learning_unit_acronym, a_tutor)})
    else:
        attributions = get_terminating_charges(APPLICATION_YEAR, a_tutor)
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
    attribution_lecturing_duration = tutor_charge.get_attribution_allocation_charge(an_attribution.tutor,
                                                                                     an_attribution.learning_unit_year,
                                                                                     component_type.LECTURING)
    attribution_practical_duration = tutor_charge.get_attribution_allocation_charge(an_attribution.tutor,
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
    form = ApplicationForm()
    application = get_application_informations(mdl_attribution.tutor_application.find_by_id(tutor_application_id))
    if application:
        data = {'charge_lecturing': application[APPLICATION_CHARGE_LECTURING].allocation_charge,
                'charge_practical': application[APPLICATION_CHARGE_PRACTICAL].allocation_charge,
                'remark': application[TUTOR_APPLICATION].remark,
                'course_summary': application[TUTOR_APPLICATION].course_summary,
                'max_charge_lecturing': application[VACANT_ATTRIBUTION_CHARGE_LECTURING],
                'max_charge_practical': application[VACANT_ATTRIBUTION_CHARGE_PRACTICAL]}
        form = ApplicationForm(initial=data)

    return render(request, "application_form.html", {
        'application': application,
        'form': form})


def format_charge(value):
    if value:
        return value.replace(',', '.')
    return 0


def save_on_new_learning_unit(request):
    new_tutor_application = create_tutor_application_from_user_learning_unit_year(request)
    form = ApplicationForm(data=request.POST)

    if form.is_valid():
        if new_tutor_application:
            new_tutor_application.course_summary = form['course_summary'].value()
            new_tutor_application.remark = form['remark'].value()
            new_tutor_application.save()

        application_charge_create(new_tutor_application,
                                  format_charge(form['charge_lecturing'].value()),
                                  component_type.LECTURING)

        application_charge_create(new_tutor_application,
                                  format_charge(form['charge_practical'].value()),
                                  component_type.PRACTICAL_EXERCISES)

        new_tutor_application.function = define_tutor_application_function(new_tutor_application,
                                                                           request)
        new_tutor_application.save()

        return home(request)
    else:
        return render(request, "application_form.html", {
            'application': get_application_informations(new_tutor_application),
            'attributions': get_terminating_charges(YEAR_OVER, new_tutor_application.tutor),
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
            tutor_application_to_save.function = define_tutor_application_function(tutor_application_to_save,
                                                                                   request)
            tutor_application_to_save.save()
        return home(request)
    else:
        return render(request, "application_form.html", {
            'application': get_application_informations(tutor_application_to_save),
            'attributions': get_terminating_charges(YEAR_OVER, tutor_application_to_save.tutor),
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


def get_learning_unit_year_vacant(a_year, an_acronym, a_tutor):
    an_academic_year = mdl_base.academic_year.find_by_year(a_year)
    learning_unit_years = mdl_base.learning_unit_year.search(an_academic_year, an_acronym, None, None)
    for a_learning_unit_year in learning_unit_years:
        if a_learning_unit_year.vacant:
            return get_new_attribution_informations(a_learning_unit_year, a_tutor)
    return None


def totally_vacant(a_learning_unit_year):
    lecturing_duration = get_learning_unit_component_duration(a_learning_unit_year, component_type.LECTURING)
    practical_duration = get_learning_unit_component_duration(a_learning_unit_year, component_type.PRACTICAL_EXERCISES)
    vacant_lecturing_charge = get_vacant_attribution_allocation_charge(a_learning_unit_year, component_type.LECTURING)
    vacant_practical_charge = get_vacant_attribution_allocation_charge(a_learning_unit_year,
                                                                       component_type.PRACTICAL_EXERCISES)
    if (lecturing_duration+practical_duration) == (vacant_lecturing_charge+vacant_practical_charge):
        return True
    return False


def is_team_application_possible(a_learning_unit_year):
    if a_learning_unit_year.team and totally_vacant(a_learning_unit_year):
        return False
    return True


def is_application_possible(a_learning_unit_year, a_tutor):
    a_tutor_application = mdl_attribution.tutor_application.find_first(a_tutor, a_learning_unit_year)
    if a_tutor_application:
        return False
    return True


def get_new_attribution_informations(a_learning_unit_year, a_tutor):
    d = {ACRONYM: a_learning_unit_year.acronym,
         TITLE: a_learning_unit_year.title,
         LECTURING_DURATION: get_learning_unit_component_duration(a_learning_unit_year, component_type.LECTURING),
         PRACTICAL_DURATION: get_learning_unit_component_duration(a_learning_unit_year, component_type.PRACTICAL_EXERCISES),
         VACANT_ATTRIBUTION_CHARGE_LECTURING: get_vacant_attribution_allocation_charge(a_learning_unit_year,
                                                                                       component_type.LECTURING),
         VACANT_ATTRIBUTION_CHARGE_PRACTICAL: get_vacant_attribution_allocation_charge(a_learning_unit_year,
                                                                                       component_type.PRACTICAL_EXERCISES),
         LEARNING_UNIT_YEAR_ID: a_learning_unit_year.id,
         TEAM: a_learning_unit_year.team,
         TEAM_APPLICATION_POSSIBLE: is_team_application_possible(a_learning_unit_year),
         APPLICATION_POSSIBLE: is_application_possible(a_learning_unit_year,a_tutor)}
    return d


def define_renew_possible(a_tutor, a_learning_unit_year):
    next_learning_unit_year = get_learning_unit_for_next_year(a_learning_unit_year)
    if is_vacant(next_learning_unit_year) and is_team_application_possible(next_learning_unit_year):
        tutor_applications = mdl_attribution.tutor_application.search(a_tutor, next_learning_unit_year)
        if tutor_applications:
            return False
        return True
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
    if learning_unit_year:
        a_new_tutor_application = mdl_attribution.tutor_application.TutorApplication()
        a_new_tutor_application.tutor = mdl_base.tutor.find_by_user(request.user)

        a_new_tutor_application.learning_unit_year = learning_unit_year
        a_new_tutor_application.remark = None
        a_new_tutor_application.course_summary = None
        a_new_tutor_application.start_date = get_start_date(learning_unit_year.academic_year)
        a_new_tutor_application.end_date = get_end_date(learning_unit_year.academic_year)

        return a_new_tutor_application
    return None


def sum_application_charge_allocation_by_component(a_tutor_application, a_component_type):
    a_learning_unit_component = mdl_base.learning_unit_component.find_first(a_tutor_application.learning_unit_year,
                                                                            a_component_type)
    attribution_charge = mdl_attribution.application_charge.find_first(a_tutor_application, a_learning_unit_component)
    if attribution_charge:
        return attribution_charge.allocation_charge
    return CHARGE_NUL


def existing_tutor_application_for_next_year(a_tutor, a_learning_unit_year):
    tutor_applications = mdl_attribution.tutor_application.search(a_tutor,
                                                                  get_learning_unit_for_next_year(a_learning_unit_year))
    if tutor_applications:
        return True

    return False


def get_first_application_tutor(a_tutor, a_learning_unit_year):
    next_learning_unit_year = get_learning_unit_for_next_year(a_learning_unit_year)
    return mdl_attribution.tutor_application.find_first(a_tutor, next_learning_unit_year)
