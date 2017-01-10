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


ONE_DECIMAL_FORMAT = "%0.1f"

MAIL_TO = 'mailto:'
STUDENT_LIST_EMAIL_END = '@listes-student.uclouvain.be'
DURATION_NUL = 0
ALLOCATION_CHARGE_NUL = 0

JSON_LEARNING_UNIT_NOTE = 'note'
JSON_LEARNING_UNIT_STATUS = 'etatExam'

JANUARY = "janvier"
JUNE = "juin"
SEPTEMBER = "septembre"


@login_required
def home(request):
    return by_year(request, datetime.datetime.now().year)


def get_person(a_user):
    return mdl_base.person.find_by_user(a_user)


def get_attribution_allocation_charge(a_tutor, a_learning_unit_year, a_component_type):
    attribution_list = mdl_attribution.attribution.search(a_tutor, a_learning_unit_year)
    tot_allocation_charge = ALLOCATION_CHARGE_NUL
    for an_attribution in attribution_list:
        a_learning_unit_components = mdl_base.learning_unit_component.search(a_learning_unit_year, a_component_type)
        for a_learning_unit_component in a_learning_unit_components:
            attribution_charges = mdl_attribution.attribution_charge.search(an_attribution, a_learning_unit_component)
            for attribution_charge in attribution_charges:
                tot_allocation_charge += attribution_charge.allocation_charge
    return tot_allocation_charge


def sum_learning_unit_year_duration(a_learning_unit_year):
    tot_duration = DURATION_NUL
    for learning_unit_component in mdl_base.learning_unit_component.search(a_learning_unit_year, None):
        if learning_unit_component.duration:
            tot_duration += learning_unit_component.duration
    return tot_duration


def is_string_not_null_empty(string):
    if string and len(string.strip()) > 0:
        return True
    return False


def get_email_students(an_acronym):
    if is_string_not_null_empty(an_acronym):
        return "{0}{1}{2}".format(MAIL_TO, an_acronym.lower(), STUDENT_LIST_EMAIL_END)
    return None


def get_schedule_url(an_acronym):
    if is_string_not_null_empty(an_acronym):
        return settings.ADE_MAIN_URL.format(settings.ADE_PROJET_NUMBER, an_acronym.lower())
    return None


def list_attributions(a_person, an_academic_year):
    results_in_charge = []
    results = mdl_attribution.attribution \
        .find_by_tutor_year_order_by_acronym_function(mdl_base.tutor.find_by_person(a_person), an_academic_year)
    for attribution in results:
        if attribution.learning_unit_year.in_charge:
            results_in_charge.append(attribution)
    return results_in_charge


def list_teaching_charge_attribution_representation(a_person, an_academic_year):
    attribution_list = []
    a_tutor = mdl_base.tutor.find_by_person(a_person)
    tot_lecturing = ALLOCATION_CHARGE_NUL
    tot_practical = ALLOCATION_CHARGE_NUL
    for an_attribution in list_attributions(a_person, an_academic_year):
        a_learning_unit_year = an_attribution.learning_unit_year
        tot_attribution_lecturing = attribution_allocation_charge(a_learning_unit_year,
                                                                  component_type.LECTURING,
                                                                  an_attribution)
        tot_attribution_practical = attribution_allocation_charge(a_learning_unit_year,
                                                                  component_type.PRACTICAL_EXERCISES,
                                                                  an_attribution)
        tot_lecturing = tot_lecturing + tot_attribution_lecturing
        tot_practical = tot_practical + tot_attribution_practical
        attribution_list.append(
            {'acronym': a_learning_unit_year.acronym,
             'title': a_learning_unit_year.title,
             'lecturing_allocation_charge':
                 ONE_DECIMAL_FORMAT % (tot_attribution_lecturing,),
             'practice_allocation_charge':
                 ONE_DECIMAL_FORMAT % (tot_attribution_practical,),
             'percentage_allocation_charge':
                 calculate_attribution_format_percentage_allocation_charge(a_learning_unit_year,
                                                                           an_attribution),
             'weight': a_learning_unit_year.credits,
             'url_schedule': get_schedule_url(a_learning_unit_year.acronym),
             'url_students_list_email': get_email_students(a_learning_unit_year.acronym),
             'function': an_attribution.function,
             'year': a_learning_unit_year.academic_year.year,
             'learning_unit_year_url': get_url_learning_unit_year(a_learning_unit_year),
             'learning_unit_year': a_learning_unit_year})

    return {'attributions': attribution_list,
            'tot_lecturing': tot_lecturing,
            'tot_practical': tot_practical}

def by_year(request, year):
    a_person = get_person(request.user)
    an_academic_year = None
    if year:
        an_academic_year = mdl_base.academic_year.find_by_year(year)
    attributions = None
    tot_lecturing = None
    tot_practical = None
    if is_tutor(a_person):
        attributions_dict = list_teaching_charge_attribution_representation(a_person, an_academic_year)
        attributions = attributions_dict['attributions']
        tot_lecturing = attributions_dict['tot_lecturing']
        tot_practical = attributions_dict['tot_practical']

    return render(request, "tutor_charge.html", {
        'user': request.user,
        'attributions': attributions,
        'formset': set_formset_years(a_person),
        'year': int(year),
        'tot_lecturing': tot_lecturing,
        'tot_practical': tot_practical})


def get_attribution_years(a_person):
    return list(mdl_attribution.attribution.find_distinct_years(mdl_base.tutor.find_by_person(a_person)))


def set_formset_years(a_person):
    AttributionFormSet = formset_factory(AttributionForm, extra=0)
    initial_data = []
    for yr in get_attribution_years(a_person):
        initial_data.append({'year': yr,
                             'next_year': yr+1})

    return AttributionFormSet(initial=initial_data)


def get_url_learning_unit_year(a_learning_unit_year):
    if a_learning_unit_year:
        if is_string_not_null_empty(a_learning_unit_year.acronym):
            return settings.UCL_URL.format(a_learning_unit_year.academic_year.year,
                                           a_learning_unit_year.acronym.lower())
    return None


def get_students(a_learning_unit_year):
    return mdl_base.learning_unit_enrollment.find_by_learningunit_enrollment(a_learning_unit_year)


@login_required
def show_students(request, a_learning_unit_year):
    students_list = []
    for learning_unit_enrollment in get_students(a_learning_unit_year):
        students_list.append(set_student_for_display(learning_unit_enrollment))
    return render(request, "students_list.html", {
        'students': students_list,
        'learning_unit_year': mdl_base.learning_unit_year.find_by_id(a_learning_unit_year), })


def get_sessions_results(a_registration_id, a_learning_unit, offer_acronym):
    results = {}
    academic_year = a_learning_unit.academic_year.year
    a_student_performance = mdl_performance.student_performance \
        .find_by_student_and_offer_year(a_registration_id, academic_year, offer_acronym)

    if a_student_performance:
        student_data = get_student_data_dict(a_student_performance)
        monAnnee = student_data['monAnnee']
        if student_data['etudiant']['noma'] == a_registration_id and monAnnee['anac'] == str(academic_year):
            monOffre = monAnnee['monOffre']
            offre = monOffre['offre']
            if offre['sigleComplet'] == offer_acronym:
                cours_list = monOffre['cours']
                nb_cours = 0
                while nb_cours < len(cours_list):
                    cours = cours_list[nb_cours]
                    if cours['sigleComplet'] == a_learning_unit.acronym:
                        get_student_results(cours, results)
                    nb_cours = nb_cours + 1
    return results


def get_student_results(cours, results):
    sessions = cours['session']
    nb_session = 0
    while nb_session < len(sessions):
        results.update({sessions[nb_session]['mois']: {
            JSON_LEARNING_UNIT_NOTE: get_value(sessions[nb_session], JSON_LEARNING_UNIT_NOTE),
            JSON_LEARNING_UNIT_STATUS: get_value(sessions[nb_session], JSON_LEARNING_UNIT_STATUS)}})
        nb_session = nb_session + 1


def get_student_data_dict(a_student_performance):
    if a_student_performance:
        data_input = json.dumps(a_student_performance.data)
        return json.loads(data_input)
    return None


def get_value(session, variable_name):
    try:
        return session[variable_name]
    except KeyError:
        return None


def get_session_value(session_results, month_session, variable_to_get):
    try:
        return session_results[month_session][variable_to_get]
    except KeyError:
        return None


def set_student_for_display(learning_unit_enrollment):
    session_results = get_sessions_results(learning_unit_enrollment.offer_enrollment.student.registration_id,
                                           learning_unit_enrollment.learning_unit_year,
                                           learning_unit_enrollment.offer_enrollment.offer_year.acronym)
    return{
        'name': "{0}, {1}".format(learning_unit_enrollment.offer_enrollment.student.person.last_name,
                                  learning_unit_enrollment.offer_enrollment.student.person.first_name),
        'program': learning_unit_enrollment.offer_enrollment.offer_year.acronym,
        'registration_id': learning_unit_enrollment.offer_enrollment.student.registration_id,
        'january_note': get_session_value(session_results, JANUARY, JSON_LEARNING_UNIT_NOTE),
        'january_status': get_session_value(session_results, JANUARY, JSON_LEARNING_UNIT_STATUS),
        'june_note': get_session_value(session_results, JUNE, JSON_LEARNING_UNIT_NOTE),
        'june_status': get_session_value(session_results, JUNE, JSON_LEARNING_UNIT_STATUS),
        'september_note': get_session_value(session_results, JUNE, JSON_LEARNING_UNIT_NOTE),
        'september_status': get_session_value(session_results, SEPTEMBER, JSON_LEARNING_UNIT_STATUS,) ,}


def is_tutor(a_person):
    if mdl_base.tutor.find_by_person(a_person):
        return True
    return False


def attribution_allocation_charge(a_learning_unit_year, a_component_type, an_attribution):

    tot_allocation_charge = ALLOCATION_CHARGE_NUL

    a_learning_unit_components = mdl_base.learning_unit_component.search(a_learning_unit_year, a_component_type)
    for a_learning_unit_component in a_learning_unit_components:
        attribution_charges = mdl_attribution.attribution_charge.search(an_attribution, a_learning_unit_component)
        for attribution_charge in attribution_charges:
            tot_allocation_charge += attribution_charge.allocation_charge

    return tot_allocation_charge


def calculate_attribution_format_percentage_allocation_charge(a_learning_unit_year, an_attribution):
    duration = sum_learning_unit_year_duration(a_learning_unit_year)
    if duration > DURATION_NUL:
        percentage = attribution_allocation_charge(a_learning_unit_year, None, an_attribution) * 100 / duration
        return ONE_DECIMAL_FORMAT % (percentage,)
    return None

