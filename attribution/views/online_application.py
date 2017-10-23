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
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test, permission_required
from django.conf import settings
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse, reverse_lazy
from django.contrib import messages
from django.utils.translation import ugettext as trans

from attribution import models as mdl_attribution
from attribution.views import tutor_charge
from base import models as mdl_base
from base.models.enums import component_type
from attribution.models.enums import function
from attribution.forms.application import ApplicationForm
from osis_common.queue import queue_sender
from attribution.utils import message_generation, permission
from osis_common.messaging import message_config, send_message as message_service
from django.shortcuts import redirect
from base.views import layout
from base.forms.base_forms import GlobalIdForm
from attribution.views.decorators.authorization import user_is_tutor_or_super_user
from django.utils.translation import ugettext_lazy as _


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
NO_CHARGE = 0

UPDATE_OPERATION = "update"
DELETE_OPERATION = "delete"


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
    a_learning_unit_year = an_attribution.learning_unit_year
    a_tutor = an_attribution.tutor

    start = an_attribution.start_year
    end = an_attribution.end_year
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
            RENEW: define_renew_possible(a_tutor, a_learning_unit_year, an_attribution.function),
            TEAM: a_learning_unit_year.team,
            START_ACADEMIC_YEAR: format_academic_year(start),
            END_ACADEMIC_YEAR: format_end_academic_year(end),
            VACANT_ATTRIBUTION_CHARGE_LECTURING:
                get_vacant_attribution_allocation_charge(next_learning_unit_year, component_type.LECTURING),
            VACANT_ATTRIBUTION_CHARGE_PRACTICAL:
                get_vacant_attribution_allocation_charge(next_learning_unit_year, component_type.PRACTICAL_EXERCISES)}


def get_application_informations(a_tutor_application):
    a_learning_unit_year = a_tutor_application.learning_unit_year
    a_tutor = a_tutor_application.tutor
    a_lecturing_duration = get_learning_unit_component_duration(a_learning_unit_year,
                                                                component_type.LECTURING)
    a_practical_duration = get_learning_unit_component_duration(a_learning_unit_year,
                                                                component_type.PRACTICAL_EXERCISES)
    lecturing_allocated = tutor_charge.attribution_allocation_charges(a_tutor,
                                                                      a_learning_unit_year,
                                                                      component_type.LECTURING)
    practical_allocated = tutor_charge.attribution_allocation_charges(a_tutor,
                                                                      a_learning_unit_year,
                                                                      component_type.PRACTICAL_EXERCISES)
    return {
        TUTOR_APPLICATION: a_tutor_application,
        LECTURING_DURATION: a_lecturing_duration,
        PRACTICAL_DURATION: a_practical_duration,
        ATTRIBUTION_CHARGE_LECTURING: lecturing_allocated,
        ATTRIBUTION_CHARGE_PRACTICAL: practical_allocated,
        APPLICATION_CHARGE_LECTURING: get_tutor_application_charge(component_type.LECTURING, a_tutor_application),
        APPLICATION_CHARGE_PRACTICAL: get_tutor_application_charge(component_type.PRACTICAL_EXERCISES,
                                                                   a_tutor_application),
        VACANT_ATTRIBUTION_CHARGE_LECTURING:
            get_vacant_attribution_allocation_charge(a_learning_unit_year, component_type.LECTURING),
        VACANT_ATTRIBUTION_CHARGE_PRACTICAL:
            get_vacant_attribution_allocation_charge(a_learning_unit_year, component_type.PRACTICAL_EXERCISES)}


def get_learning_unit_component_duration(a_learning_unit_year, a_component_type):
    a_learning_unit_components = mdl_base.learning_unit_component.search(a_learning_unit_year, a_component_type)
    tot_duration = 0
    for a_learning_unit_component in a_learning_unit_components:
        if a_learning_unit_component.duration:
            coefficient_repetition = 1
            if a_learning_unit_component.coefficient_repetition:
                coefficient_repetition = a_learning_unit_component.coefficient_repetition
            tot_duration += (a_learning_unit_component.duration * coefficient_repetition)
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
    return tutor_charge.attribution_allocation_charges(None,
                                                       a_learning_unit_year,
                                                       component_type.LECTURING) \
           + tutor_charge.attribution_allocation_charges(None,
                                                         a_learning_unit_year,
                                                         component_type.PRACTICAL_EXERCISES)


def sum_tutor_application_allocated_charges(a_tutor_application):
    return sum_application_charge_allocation_by_component(a_tutor_application, component_type.LECTURING) \
           + sum_application_charge_allocation_by_component(a_tutor_application, component_type.PRACTICAL_EXERCISES)


def get_vacant_attribution_allocation_charge(a_learning_unit_year, a_component_type):
    if a_learning_unit_year:
        return get_learning_unit_component_duration(a_learning_unit_year, a_component_type) - tutor_charge.attribution_allocation_charges(None, a_learning_unit_year, a_component_type)
    return NO_CHARGE


def get_tutor_applications(a_year, a_tutor):
    application_list = []
    an_academic_year = mdl_base.academic_year.find_by_year(a_year)
    if an_academic_year:
        tutor_applications = mdl_attribution.tutor_application\
            .find_tutor_by_tutor_year(a_tutor, an_academic_year)
        if tutor_applications:
            for tutor_application in tutor_applications:
                application_list.append(get_application_informations(tutor_application))
    return application_list


def define_tutor_application_function(a_tutor_application):
    if a_tutor_application.function and a_tutor_application.function == function.COORDINATOR:
        return function.COORDINATOR
    else:
        a_learning_unit_year = a_tutor_application.learning_unit_year
        if sum_tutor_application_allocated_charges(a_tutor_application) == tutor_charge.sum_learning_unit_year_duration(a_learning_unit_year):
            return function.HOLDER
        return function.CO_HOLDER


def create_application_charge(a_new_tutor_application, charge_duration, a_component_type):
    a_learning_unit_component = mdl_base.learning_unit_component\
        .find_by_learning_year_type(a_new_tutor_application.learning_unit_year, a_component_type)

    if a_learning_unit_component:
        a_new_application_charge = mdl_attribution.application_charge.\
            ApplicationCharge(tutor_application=a_new_tutor_application,
                              learning_unit_component=a_learning_unit_component,
                              allocation_charge=charge_duration)
        a_new_application_charge.save()
        return a_new_application_charge
    return None


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
        attributions = mdl_attribution.attribution\
            .find_by_tutor_year_order_by_acronym_function(a_tutor, an_academic_year)
        attributions_vacant = []
        for attribution in attributions:
            next_learning_unit_year = get_learning_unit_for_next_year(attribution.learning_unit_year)
            a_function = duplicated_function(attribution, attributions)
            if next_learning_unit_year and not existing_tutor_application_for_next_year(a_tutor,
                                                                                        attribution.learning_unit_year,
                                                                                        a_function) \
                and next_learning_unit_year.in_charge and not is_deputy_function(attribution.function):
                attributions_vacant.append(attribution)
        return get_attribution_data(attributions_vacant)
    return []


@login_required
@permission_required('attribution.can_access_attribution_application', raise_exception=True)
def home(request):
    a_tutor = mdl_base.tutor.find_by_user(request.user)
    return applications_form(a_tutor, request)


def applications_form(a_tutor, request, mail_confirmation=None):
    application_year = mdl_base.academic_year.find_next_academic_year()
    attributions = get_attributions_allocated(application_year, a_tutor)
    tot_lecturing = 0
    tot_practical = 0
    if attributions:
        for attribution_informations in attributions:
            tot_lecturing = tot_lecturing + attribution_informations[ATTRIBUTION_CHARGE_LECTURING]
            tot_practical = tot_practical + attribution_informations[ATTRIBUTION_CHARGE_PRACTICAL]
    return render(request, "attribution_applications.html", {
        'mail_confirmation': mail_confirmation,
        'a_tutor': a_tutor,
        'applications': get_tutor_applications(application_year, a_tutor),
        'attributions': attributions,
        'academic_year': "{0}-{1}".format(application_year, application_year + 1),
        'tot_lecturing': tot_lecturing,
        'tot_practical': tot_practical})


def get_tutor_application_charge(a_component_type, a_tutor_application):
    a_learning_unit_component = mdl_base.learning_unit_component\
        .find_by_learning_year_type(a_tutor_application.learning_unit_year, a_component_type)

    return mdl_attribution.application_charge\
        .find_by_tutor_application_learning_unit_component(a_tutor_application, a_learning_unit_component)


def get_application_charge(a_tutor, a_learning_unit_year, a_component_type):
    for an_tutor_application in mdl_attribution.tutor_application.search(a_tutor, a_learning_unit_year, None):
        for a_learning_unit_component in mdl_base.learning_unit_component.search(a_learning_unit_year,
                                                                                 a_component_type):
            application_charges = mdl_attribution.application_charge.search(an_tutor_application,
                                                                            a_learning_unit_component)
            for application_charge in application_charges:
                return application_charge

    return None


@login_required
@permission_required('attribution.can_access_attribution_application', raise_exception=True)
def delete(request, tutor_application_id):
    tutor_application_to_delete = mdl_attribution.tutor_application.find_by_id(tutor_application_id)
    a_tutor = tutor_application_to_delete.tutor
    if tutor_application_to_delete:
        queue_sender\
            .send_message(settings.QUEUES.get('QUEUES_NAME').get('ATTRIBUTION'),
                          message_generation.generate_message_from_tutor_application(
                              tutor_application_to_delete,
                              tutor_application_to_delete.function,
                              DELETE_OPERATION))

        tutor_application_to_delete.delete()

    return HttpResponseRedirect(reverse('visualize_tutor_applications',
                                        kwargs={'global_id': a_tutor.person.global_id}))


@login_required
@user_passes_test(permission.is_online_application_opened, login_url=reverse_lazy('outside_applications_period'))
@permission_required('attribution.can_access_attribution_application', raise_exception=True)
def attribution_application_form(request, global_id):
    a_tutor = mdl_base.tutor.find_by_person_global_id(global_id)
    last_year = get_last_year()

    attributions = get_terminating_charges(last_year, a_tutor)
    application_year = mdl_base.academic_year.find_next_academic_year()
    return render(request, "attribution_application_form.html", {
        'a_tutor': a_tutor,
        'application': None,
        'attributions': attributions,
        'application_academic_year': "{0}-{1}".format(application_year, application_year + 1),
        'over_academic_year': "{0}-{1}".format(last_year, last_year + 1)})


@login_required
def search(request, global_id):
    learning_unit_acronym = request.GET['learning_unit_acronym']
    a_tutor = mdl_base.tutor.find_by_person_global_id(global_id)
    application_year = mdl_base.academic_year.find_next_academic_year()
    if learning_unit_acronym and len(learning_unit_acronym.strip()) > 0:
        return render(request, "attribution_vacant.html", {
            'a_tutor': a_tutor,
            'attribution': get_learning_unit_year_vacant(application_year, learning_unit_acronym, a_tutor)})
    else:
        attributions = get_terminating_charges(application_year, a_tutor)
        return render(request, "attribution_application_form.html", {
            'a_tutor': a_tutor,
            'application': None,
            'attributions': attributions})


@login_required
@user_passes_test(permission.is_online_application_opened, login_url=reverse_lazy('outside_applications_period'))
@permission_required('attribution.can_access_attribution_application', raise_exception=True)
def renew(request):
    for key, value in request.POST.items():
        if key.startswith(ATTRIBUTION_ID_NAME):
            attribution_id = int(key.replace(ATTRIBUTION_ID_NAME, ''))
            an_attribution_to_renew = mdl_attribution.attribution.find_by_id(int(attribution_id))
            if an_attribution_to_renew:
                create_tutor_application_from_attribution(an_attribution_to_renew)

    return HttpResponseRedirect(reverse('visualize_tutor_applications', kwargs={'global_id': a_tutor.person.global_id}))


def create_tutor_application_from_attribution(an_attribution):
    attribution_lecturing_duration = get_attribution_allocation_charge(an_attribution,
                                                                       component_type.LECTURING)
    attribution_practical_duration = get_attribution_allocation_charge(an_attribution,
                                                                       component_type.PRACTICAL_EXERCISES)
    next_academic_year = mdl_base.academic_year.find_by_year(an_attribution.learning_unit_year.academic_year.year+1)

    next_learning_unit_years = mdl_base.learning_unit_year.search(next_academic_year,
                                                                  None,
                                                                  an_attribution.learning_unit_year.learning_unit)
    next_learning_unit_year = None
    if next_learning_unit_years:
        next_learning_unit_year = next_learning_unit_years[0]
    a_new_tutor_application = mdl_attribution.tutor_application.TutorApplication()
    a_new_tutor_application.tutor = an_attribution.tutor
    a_new_tutor_application.function = an_attribution.function
    a_new_tutor_application.learning_unit_year = next_learning_unit_year
    a_new_tutor_application.remark = None
    a_new_tutor_application.course_summary = None
    a_new_tutor_application.start_year = next_learning_unit_year.academic_year.year
    a_new_tutor_application.end_year = next_learning_unit_year.academic_year.year
    a_new_tutor_application.save()

    application_charge_lecturing = create_application_charge(a_new_tutor_application,
                                                             attribution_lecturing_duration,
                                                             component_type.LECTURING)
    application_charge_practical = create_application_charge(a_new_tutor_application,
                                                             attribution_practical_duration,
                                                             component_type.PRACTICAL_EXERCISES)
    a_new_tutor_application.function = define_tutor_application_function(a_new_tutor_application)
    a_new_tutor_application.save()

    queue_sender.send_message(
        settings.QUEUES.get('QUEUES_NAME').get('ATTRIBUTION'),
        message_generation.generate_message_from_application_charge(
            application_charge_lecturing,
            UPDATE_OPERATION,
            a_new_tutor_application.function))

    queue_sender.send_message(settings.QUEUES.get('QUEUES_NAME').get('ATTRIBUTION'),
                              message_generation.generate_message_from_application_charge(
                                  application_charge_practical,
                                  UPDATE_OPERATION,
                                  a_new_tutor_application.function))
    return a_new_tutor_application


@login_required
@user_passes_test(permission.is_online_application_opened, login_url=reverse_lazy('outside_applications_period'))
@permission_required('attribution.can_access_attribution_application', raise_exception=True)
def edit(request, tutor_application_id):
    form = ApplicationForm()
    application = get_application_informations(mdl_attribution.tutor_application.find_by_id(tutor_application_id))
    if application:
        charge_lecturing = application[APPLICATION_CHARGE_LECTURING].allocation_charge if application[APPLICATION_CHARGE_LECTURING] else NO_CHARGE
        charge_practical = application[APPLICATION_CHARGE_PRACTICAL].allocation_charge if application[APPLICATION_CHARGE_PRACTICAL] else NO_CHARGE

        data = {'charge_lecturing': charge_lecturing,
                'charge_practical': charge_practical,
                'remark': application[TUTOR_APPLICATION].remark,
                'course_summary': application[TUTOR_APPLICATION].course_summary,
                'max_charge_lecturing': application[VACANT_ATTRIBUTION_CHARGE_LECTURING],
                'max_charge_practical': application[VACANT_ATTRIBUTION_CHARGE_PRACTICAL]}
        form = ApplicationForm(initial=data)

    return render(request, "application_form.html", {
        'a_tutor': application[TUTOR_APPLICATION].tutor,
        'application': application,
        'form': form})


def format_charge(value):
    if value:
        return value.replace(',', '.')
    return 0


@login_required
@user_passes_test(permission.is_online_application_opened, login_url=reverse_lazy('outside_applications_period'))
@permission_required('attribution.can_access_attribution_application', raise_exception=True)
def save_on_new_learning_unit(request, tutor_global_id):
    new_tutor_application = create_tutor_application_from_user_learning_unit_year(
        tutor_global_id, request.POST.get('learning_unit_year_id'))
    form = ApplicationForm(data=request.POST)

    if form.is_valid():
        if new_tutor_application:
            new_tutor_application.course_summary = form['course_summary'].value()
            new_tutor_application.remark = form['remark'].value()
            new_tutor_application.save()

        application_charge_lecturing = application_charge_create(new_tutor_application,
                                                                 format_charge(form['charge_lecturing'].value()),
                                                                 component_type.LECTURING)

        application_charge_practical = application_charge_create(new_tutor_application,
                                                                 format_charge(form['charge_practical'].value()),
                                                                 component_type.PRACTICAL_EXERCISES)

        new_tutor_application.function = define_tutor_application_function(new_tutor_application)
        new_tutor_application.save()
        queue_sender.send_message(
            settings.QUEUES.get('QUEUES_NAME').get('ATTRIBUTION'),
            message_generation.generate_message_from_application_charge(
                application_charge_lecturing,
                UPDATE_OPERATION,
                define_tutor_application_function(new_tutor_application)))

        queue_sender.send_message(settings.QUEUES.get('QUEUES_NAME').get('ATTRIBUTION'),
                                  message_generation.generate_message_from_application_charge(
                                      application_charge_practical,
                                      UPDATE_OPERATION,
                                      define_tutor_application_function(new_tutor_application)))

        return HttpResponseRedirect(reverse('visualize_tutor_applications',
                                            kwargs={'global_id': tutor_global_id}))
    else:
        return render(request, "application_form.html", {
            'a_tutor': application[TUTOR_APPLICATION].tutor,
            'application': get_application_informations(new_tutor_application),
            'attributions': get_terminating_charges(get_last_year(), new_tutor_application.tutor),
            'form': form})


def create_tutor_application_from_user_learning_unit_year(tutor_global_id, a_learning_unit_year_id):
    new_tutor_application = mdl_attribution.tutor_application.TutorApplication()
    new_tutor_application.tutor = mdl_base.tutor.find_by_person_global_id(tutor_global_id)
    new_tutor_application.learning_unit_year = mdl_base.learning_unit_year.find_by_id(a_learning_unit_year_id)
    new_tutor_application.start_year = new_tutor_application.learning_unit_year.academic_year.year
    new_tutor_application.end_year = new_tutor_application.learning_unit_year.academic_year.year
    return new_tutor_application


@login_required
@user_passes_test(permission.is_online_application_opened, login_url=reverse_lazy('outside_applications_period'))
@permission_required('attribution.can_access_attribution_application', raise_exception=True)
def save(request, tutor_application_id):
    tutor_application_to_save = mdl_attribution.tutor_application.find_by_id(tutor_application_id)
    a_tutor = tutor_application_to_save.tutor
    form = ApplicationForm(data=request.POST)

    if form.is_valid():
        application_charge_lecturing = allocation_charge_update(request.POST.get('application_charge_lecturing_id'),
                                                                form['charge_lecturing'].value().replace(',', '.'))
        application_charge_practical = allocation_charge_update(request.POST.get('application_charge_practical_id'),
                                                                form['charge_practical'].value().replace(',', '.'))

        if tutor_application_to_save:
            tutor_application_to_save.course_summary = form['course_summary'].value()
            tutor_application_to_save.remark = form['remark'].value()
            tutor_application_to_save.function = define_tutor_application_function(tutor_application_to_save)
            tutor_application_to_save.save()
            application_charge_lecturing.tutor_application = tutor_application_to_save
            application_charge_practical.tutor_application = tutor_application_to_save
        queue_sender.send_message(settings.QUEUES.get('QUEUES_NAME').get('ATTRIBUTION'),
                                  message_generation.generate_message_from_application_charge(application_charge_lecturing,
                                                                                              UPDATE_OPERATION,
                                                                                              tutor_application_to_save.function))
        queue_sender.send_message(settings.QUEUES.get('QUEUES_NAME').get('ATTRIBUTION'),
                                  message_generation.generate_message_from_application_charge(application_charge_practical,
                                                                                              UPDATE_OPERATION,
                                                                                              tutor_application_to_save.function))

        return HttpResponseRedirect(reverse('visualize_tutor_applications', kwargs={'global_id': a_tutor.person.global_id}))

    else:
        return render(request, "application_form.html", {
            'a_tutor': application[TUTOR_APPLICATION].tutor,
            'application': get_application_informations(tutor_application_to_save),
            'attributions': get_terminating_charges(get_last_year(), tutor_application_to_save.tutor),
            'form': form})


def application_charge_create(a_tutor_application, a_charge, a_component_type):
    a_learning_unit_year = a_tutor_application.learning_unit_year
    a_learning_unit_component = mdl_base.learning_unit_component.find_by_learning_year_type(a_learning_unit_year,
                                                                                            a_component_type)
    if a_tutor_application and a_learning_unit_component and a_learning_unit_year:
        application_charge = mdl_attribution.application_charge\
            .ApplicationCharge(tutor_application=a_tutor_application,
                               learning_unit_component=a_learning_unit_component,
                               allocation_charge=a_charge)
        application_charge.save()
        return application_charge


def allocation_charge_update(an_application_charge_id, a_field_value):
    if an_application_charge_id:
        application_charge = mdl_attribution.application_charge.find_by_id(an_application_charge_id)
        if application_charge and a_field_value:
            application_charge.allocation_charge = a_field_value
            application_charge.save()
            return application_charge
    return None


def get_learning_unit_year_vacant(a_year, an_acronym, a_tutor):
    an_academic_year = mdl_base.academic_year.find_by_year(a_year)
    learning_unit_years = mdl_base.learning_unit_year.search(an_academic_year, an_acronym, None)
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
    tutor_applications = mdl_attribution.tutor_application.search(a_tutor, a_learning_unit_year, None)
    if tutor_applications.exists():
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
         APPLICATION_POSSIBLE: is_application_possible(a_learning_unit_year, a_tutor)}
    return d


def define_renew_possible(a_tutor, a_learning_unit_year, a_function):
    next_learning_unit_year = get_learning_unit_for_next_year(a_learning_unit_year)
    if is_vacant(next_learning_unit_year) and is_team_application_possible(next_learning_unit_year):
        tutor_applications = mdl_attribution.tutor_application.search(a_tutor, next_learning_unit_year, a_function)
        if tutor_applications:
            return False
        return True
    return False


@login_required
def new(request, global_id):
    a_tutor = mdl_base.tutor.find_by_person_global_id(global_id)
    a_learning_unit_year_id = request.POST.get('learning_unit_year_id')
    tutor_application_to_save = None
    learning_unit_year = None
    if a_learning_unit_year_id:
        learning_unit_year = mdl_base.learning_unit_year.find_by_id(a_learning_unit_year_id)
        tutor_application_to_save = create_tutor_application_from_learning_unit_year(learning_unit_year, a_tutor)
    form = ApplicationForm()
    if tutor_application_to_save:
        data = {'charge_lecturing': get_vacant_attribution_allocation_charge(learning_unit_year,
                                                                             component_type.LECTURING),
                'charge_practical': get_vacant_attribution_allocation_charge(learning_unit_year,
                                                                             component_type.PRACTICAL_EXERCISES),
                'remark': None,
                'course_summary': None,
                'max_charge_lecturing': get_learning_unit_component_duration(learning_unit_year,
                                                                             component_type.LECTURING),
                'max_charge_practical': get_learning_unit_component_duration(learning_unit_year,
                                                                             component_type.PRACTICAL_EXERCISES)}
        form = ApplicationForm(initial=data)
    return render(request, "application_form.html", {
        'a_tutor': a_tutor,
        'application': get_application_informations(tutor_application_to_save),
        'form': form})


def create_tutor_application_from_learning_unit_year(a_learning_unit_year=None, a_tutor=None):
    if a_learning_unit_year:
        a_new_tutor_application = mdl_attribution.tutor_application.TutorApplication()
        a_new_tutor_application.tutor = a_tutor

        a_new_tutor_application.learning_unit_year = a_learning_unit_year
        a_new_tutor_application.remark = None
        a_new_tutor_application.course_summary = None
        a_new_tutor_application.start_year = a_learning_unit_year.academic_year.year
        a_new_tutor_application.end_year = a_learning_unit_year.academic_year.year

        return a_new_tutor_application
    return None


def sum_application_charge_allocation_by_component(a_tutor_application, a_component_type):
    a_learning_unit_component = mdl_base.learning_unit_component\
        .find_by_learning_year_type(a_tutor_application.learning_unit_year, a_component_type)
    attribution_charge = mdl_attribution.application_charge\
        .find_by_tutor_application_learning_unit_component(a_tutor_application, a_learning_unit_component)
    if attribution_charge:
        return attribution_charge.allocation_charge
    return NO_CHARGE


def existing_tutor_application_for_next_year(a_tutor, a_learning_unit_year, a_function):
    tutor_applications = mdl_attribution.tutor_application.search(a_tutor,
                                                                  get_learning_unit_for_next_year(a_learning_unit_year),
                                                                  a_function)
    if tutor_applications:
        return True

    return False


def get_last_year():
    application_year = mdl_base.academic_year.find_next_academic_year()
    if application_year:
        return application_year - 1


def get_next_year():
    application_year = mdl_base.academic_year.find_next_academic_year()
    if application_year:
        return application_year + 1


@login_required
@permission_required('attribution.can_access_attribution_application', raise_exception=True)
def outside_period(request):
    text = trans('application_denied')
    messages.add_message(request, messages.WARNING, "%s" % text)
    return render(request, "attribution_access_denied.html")


def format_academic_year(a_year):
    if a_year:
        return "{0}-{1}".format(a_year, a_year+1)
    return ""


def format_end_academic_year(a_year):
    if a_year:
        return "{0}-{1}".format(a_year, a_year+1)
    return ""


def duplicated_function(current_attribution, attributions):
    for attribution in attributions:
        if attribution != current_attribution \
                and attribution.learning_unit_year == current_attribution.learning_unit_year:
            return current_attribution.function
    return None


def get_attribution_allocation_charge(an_attribution, a_component_type):
    a_learning_unit_year = an_attribution.learning_unit_year
    tot_allocation_charge = NO_CHARGE
    a_learning_unit_components = mdl_base.learning_unit_component.search(a_learning_unit_year, a_component_type)
    for a_learning_unit_component in a_learning_unit_components:
        attribution_charges = mdl_attribution.attribution_charge.search(an_attribution, a_learning_unit_component)
        for attribution_charge in attribution_charges:
            tot_allocation_charge += attribution_charge.allocation_charge
    return tot_allocation_charge


def is_deputy_function(a_function):
    if a_function and \
        (a_function == function.DEPUTY or
         a_function == function.DEPUTY_AUTHORITY or
         a_function == function.DEPUTY_SABBATICAL or
         a_function == function.DEPUTY_TEMPORARY):
        return True
    return False


@login_required
@permission_required('attribution.can_access_attribution_application', raise_exception=True)
@user_is_tutor_or_super_user
def applications_confirmation(request, global_id):
    a_tutor = mdl_base.tutor.find_by_person_global_id(global_id)
    application_year = mdl_base.academic_year.find_next_academic_year()
    send_mail_with_applications(application_year, a_tutor)
    return mail_applications_sent(request, global_id)


def send_mail_with_applications(application_year, a_tutor):
    applications = get_tutor_applications(application_year, a_tutor)

    html_template_ref = 'applications_confirmation_html'
    txt_template_ref = 'applications_confirmation_txt'

    tutor_person = a_tutor.person
    receivers = [message_config.create_receiver(tutor_person.id, tutor_person.email, tutor_person.language)]
    template_base_data = {'first_name': tutor_person.first_name,
                          'last_name': tutor_person.last_name,
                          'applications': get_applications_txt(applications)
                          }
    tables = None
    message_content = message_config.create_message_content(html_template_ref, txt_template_ref,
                                                            tables, receivers, template_base_data, None)
    return message_service.send_messages(message_content)


def get_applications_txt(applications):
    txt = "\n"
    for application in applications:
        txt += get_application_detail_line(application)

    return txt


def get_application_detail_line(application):
    acronym = None
    vol_lecturing = 0
    vol_practical = 0

    if application[APPLICATION_CHARGE_LECTURING]:
        acronym = application[APPLICATION_CHARGE_LECTURING].learning_unit_component.learning_unit_year.acronym
        vol_lecturing = application[APPLICATION_CHARGE_LECTURING].allocation_charge
    if application[APPLICATION_CHARGE_PRACTICAL]:
        acronym = application[APPLICATION_CHARGE_PRACTICAL].learning_unit_component.learning_unit_year.acronym
        vol_practical = application[APPLICATION_CHARGE_PRACTICAL].allocation_charge
    return "*\t{}\t{}\t{}\n".format(acronym, vol_lecturing, vol_practical)


@login_required
@permission_required('base.is_faculty_administrator', raise_exception=True)
def applications_administration(request):
    return layout.render(request, 'admin/applications_administration.html')


@login_required
@permission_required('base.is_faculty_administrator', raise_exception=True)
def select_tutor_applications(request):
    if request.method == "POST":
        form = GlobalIdForm(request.POST)
        if form.is_valid():
            global_id = form.cleaned_data['global_id']
            return visualize_tutor_applications(request, global_id)
    else:
        form = GlobalIdForm()
    return layout.render(request, "admin/applications_administration.html", {"form": form})


@login_required
@permission_required('base.is_faculty_administrator', raise_exception=True)
@user_is_tutor_or_super_user
def visualize_tutor_applications(request, global_id):
    a_tutor = mdl_base.tutor.find_by_person_global_id(global_id)
    return applications_form(a_tutor, request)


@login_required
@permission_required('base.is_faculty_administrator', raise_exception=True)
@user_is_tutor_or_super_user
def mail_applications_sent(request, global_id):
    mail_confirmation = _('applications_mail_sent')
    a_tutor = mdl_base.tutor.find_by_person_global_id(global_id)
    return applications_form(a_tutor, request, mail_confirmation)
