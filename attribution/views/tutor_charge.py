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
import datetime

from django.conf import settings
from django.forms import formset_factory
from django.shortcuts import render

from performance import models as mdl_performance
from base import models as mdl_base
from attribution import models as mdl_attribution
from base.models.enums import component_type
from attribution.forms.attribution import AttributionForm
from base.forms.base_forms import GlobalIdForm
from base.views import layout
from django.contrib.auth.decorators import login_required, permission_required
import json
import requests


ONE_DECIMAL_FORMAT = "%0.1f"

MAIL_TO = 'mailto:'
STUDENT_LIST_EMAIL_END = '@listes-student.uclouvain.be'
DURATION_NUL = 0
NO_ALLOCATION_CHARGE = 0

JSON_LEARNING_UNIT_NOTE = 'note'
JSON_LEARNING_UNIT_STATUS = 'etatExam'

JANUARY = "janvier"
JUNE = "juin"
SEPTEMBER = "septembre"

ATTRIBUTIONS_TUTOR_ALLOCATION_PATH = 'resources/AllocationCharges/tutors/{global_id}/{year}'


@login_required
@permission_required('attribution.can_access_attribution', raise_exception=True)
def home(request):
    a_person = get_person(request.user)
    if a_person:
        global_id = a_person.global_id
    else:
        global_id = None
    return by_year(request, get_current_academic_year(), global_id)


def get_current_academic_year():
    a_year = datetime.datetime.now().year
    current_academic_year = mdl_base.academic_year.current_academic_year()
    if current_academic_year:
        a_year = current_academic_year.year
    return a_year


def get_person(a_user):
    return mdl_base.person.find_by_user(a_user)


def attribution_allocation_charges(a_tutor, a_learning_unit_year, a_component_type):
    attribution_list = mdl_attribution.attribution.search(a_tutor, a_learning_unit_year)
    tot_allocation_charge = NO_ALLOCATION_CHARGE
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
        return settings.ATTRIBUTION_CONFIG.get('TIME_TABLE_URL').\
            format(settings.ATTRIBUTION_CONFIG.get('TIME_TABLE_NUMBER'), an_acronym.lower())
    return None


def list_attributions(a_person, an_academic_year):
    results_in_charge = []
    results = mdl_attribution.attribution \
        .find_by_tutor_year_order_by_acronym_function(mdl_base.tutor.find_by_person(a_person), an_academic_year)
    for attribution in results:
        if attribution.learning_unit_year.in_charge:
            results_in_charge.append(attribution)
    return results_in_charge


def list_teaching_charge(a_person, an_academic_year):
    attribution_list = []
    tot_lecturing = NO_ALLOCATION_CHARGE
    tot_practical = NO_ALLOCATION_CHARGE
    attributions_charge_duration = get_attributions_charge_duration(a_person, an_academic_year)
    for an_attribution in list_attributions(a_person, an_academic_year):
        a_learning_unit_year = an_attribution.learning_unit_year

        learning_unit_attribution_charge_duration = \
            attributions_charge_duration.get(str(an_attribution.external_id), {})

        lecturing_charge = float(learning_unit_attribution_charge_duration.get("lecturing_charge", 0))
        practical_charge = float(learning_unit_attribution_charge_duration.get("practical_charge", 0))
        learning_unit_charge = float(learning_unit_attribution_charge_duration.get("learning_unit_charge", 0))

        tot_lecturing = tot_lecturing + lecturing_charge
        tot_practical = tot_practical + practical_charge
        attribution_list.append(
            {'acronym': a_learning_unit_year.acronym,
             'title': a_learning_unit_year.title,
             'start_year': an_attribution.start_year,
             'lecturing_allocation_charge':
                 ONE_DECIMAL_FORMAT % (lecturing_charge,),
             'practice_allocation_charge':
                 ONE_DECIMAL_FORMAT % (practical_charge,),
             'percentage_allocation_charge':
                 calculate_attribution_format_percentage_allocation_charge(lecturing_charge, practical_charge,
                                                                           learning_unit_charge),
             'weight': a_learning_unit_year.credits,
             'url_schedule': get_schedule_url(a_learning_unit_year.acronym),
             'url_students_list_email': get_email_students(a_learning_unit_year.acronym),
             'function': an_attribution.function,
             'year': a_learning_unit_year.academic_year.year,
             'learning_unit_year_url': get_url_learning_unit_year(a_learning_unit_year),
             'learning_unit_year': a_learning_unit_year,
             'tutor_id': an_attribution.tutor.id})
    if len(attribution_list) == 0:
        attribution_list = None
    return {'attributions': attribution_list,
            'tot_lecturing': tot_lecturing,
            'tot_practical': tot_practical,
            'error': attributions_charge_duration.get('error', False)}


@login_required
@permission_required('attribution.can_access_attribution', raise_exception=True)
def by_year(request, year, a_global_id):
    return render(request, "tutor_charge.html", load_teaching_charge_data(a_global_id, request, year))


@login_required
@permission_required('base.is_faculty_administrator', raise_exception=True)
def by_year_admin(request, year, a_global_id):
    return render(request, "tutor_charge_admin.html", load_teaching_charge_data(a_global_id, request, year))


def load_teaching_charge_data(a_global_id, request, year):
    if a_global_id:
        a_person = mdl_base.person.find_by_global_id(a_global_id)
    else:
        a_person = get_person(request.user)
    return get_teaching_charge_data(a_person, year)


def get_teaching_charge_data(a_person, year):
    an_academic_year = None
    if year:
        an_academic_year = mdl_base.academic_year.find_by_year(year)
    attributions = None
    tot_lecturing = None
    tot_practical = None
    error = False
    if is_tutor(a_person):
        attributions_dict = list_teaching_charge(a_person, an_academic_year)
        attributions = attributions_dict['attributions']
        tot_lecturing = attributions_dict['tot_lecturing']
        tot_practical = attributions_dict['tot_practical']
        error = attributions_dict['error']
    a_user = None
    if a_person:
        a_user = a_person.user
    data = {'user': a_user,
            'attributions': attributions,
            'formset': set_formset_years(a_person),
            'year': int(year),
            'tot_lecturing': tot_lecturing,
            'tot_practical': tot_practical,
            'academic_year': an_academic_year,
            'global_id': a_person.global_id,
            'error': error}
    return data


def get_attribution_years(a_person):
    return list(mdl_attribution.attribution.find_distinct_years(mdl_base.tutor.find_by_person(a_person)))


def set_formset_years(a_person):
    AttributionFormSet = formset_factory(AttributionForm, extra=0)
    initial_data = []
    for yr in get_attribution_years(a_person):
        initial_data.append({'year': yr,
                             'next_year': str(yr+1)[-2:]})

    return AttributionFormSet(initial=initial_data)


def get_url_learning_unit_year(a_learning_unit_year):
    if a_learning_unit_year and is_string_not_null_empty(a_learning_unit_year.acronym):
        return settings.ATTRIBUTION_CONFIG.get('CATALOG_URL').format(a_learning_unit_year.academic_year.year,
                                                                     a_learning_unit_year.acronym.lower())
    return None


def get_students(a_learning_unit_year_id, a_tutor):
    a_learning_unit_year = mdl_base.learning_unit_year.find_by_id(a_learning_unit_year_id)
    return get_learning_unit_years_list(a_learning_unit_year, a_tutor)


def _load_students(a_learning_unit_year, a_tutor, request):
    students_list = []
    request_tutor = mdl_base.tutor.find_by_id(a_tutor)
    for learning_unit_enrollment in get_students(a_learning_unit_year, get_person(request_tutor.person.user)):
        students_list.append(set_student_for_display(learning_unit_enrollment))

    return {'global_id': request_tutor.person.global_id,
            'students': students_list,
            'learning_unit_year': mdl_base.learning_unit_year.find_by_id(a_learning_unit_year), }


@login_required
@permission_required('base.is_faculty_administrator', raise_exception=True)
def show_students_admin(request, a_learning_unit_year, a_tutor):
    return render(request, "students_list_admin.html",
                  _load_students(a_learning_unit_year, a_tutor, request))


@login_required
@permission_required('attribution.can_access_attribution', raise_exception=True)
def show_students(request, a_learning_unit_year, a_tutor):
    return render(request, "students_list.html",
                  _load_students(a_learning_unit_year, a_tutor, request))


def get_sessions_results(a_registration_id, a_learning_unit_year, offer_acronym):
    results = {}
    academic_year = a_learning_unit_year.academic_year.year
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
                if cours_list:
                    nb_cours = 0
                    while nb_cours < len(cours_list):
                        cours = cours_list[nb_cours]
                        if cours['sigleComplet'] == a_learning_unit_year.acronym:
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
        'email': learning_unit_enrollment.offer_enrollment.student.person.email,
        'program': learning_unit_enrollment.offer_enrollment.offer_year.acronym,
        'acronym': learning_unit_enrollment.learning_unit_year.acronym,
        'registration_id': learning_unit_enrollment.offer_enrollment.student.registration_id,
        'january_note': get_session_value(session_results, JANUARY, JSON_LEARNING_UNIT_NOTE),
        'january_status': get_session_value(session_results, JANUARY, JSON_LEARNING_UNIT_STATUS),
        'june_note': get_session_value(session_results, JUNE, JSON_LEARNING_UNIT_NOTE),
        'june_status': get_session_value(session_results, JUNE, JSON_LEARNING_UNIT_STATUS),
        'september_note': get_session_value(session_results, SEPTEMBER, JSON_LEARNING_UNIT_NOTE),
        'september_status': get_session_value(session_results, SEPTEMBER, JSON_LEARNING_UNIT_STATUS,), }


def is_tutor(a_person):
    if mdl_base.tutor.find_by_person(a_person):
        return True
    return False


def attribution_allocation_charge(a_learning_unit_year, a_component_type, an_attribution):

    tot_allocation_charge = NO_ALLOCATION_CHARGE

    a_learning_unit_components = mdl_base.learning_unit_component.search(a_learning_unit_year, a_component_type)
    for a_learning_unit_component in a_learning_unit_components:
        attribution_charges = mdl_attribution.attribution_charge.search(an_attribution, a_learning_unit_component)
        for attribution_charge in attribution_charges:
            tot_allocation_charge += attribution_charge.allocation_charge

    return tot_allocation_charge


def calculate_attribution_format_percentage_allocation_charge(lecturing_charge, practical_charge, learning_unit_charge):
    if learning_unit_charge > DURATION_NUL:
        percentage = (lecturing_charge + practical_charge) * 100 / learning_unit_charge
        return ONE_DECIMAL_FORMAT % (percentage,)
    return None


def get_learning_unit_years_list(a_learning_unit_year, a_tutor):
    # Pour trouver les inscriptions aux partims/classe identifiables dans learning_unit_year par leurs
    # Par exemple l'acronym du partim pour lu LCOPS1124 c'est LCOPS1124L
    learning_unit_years_allocated = []
    for lu in mdl_base.learning_unit_year.find_by_acronym(a_learning_unit_year.acronym,
                                                          a_learning_unit_year.academic_year):
        learning_unit_years_allocated.append(lu)

    return mdl_base.learning_unit_enrollment.find_by_learning_unit_years(learning_unit_years_allocated)


@login_required
@permission_required('base.is_faculty_administrator', raise_exception=True)
def attribution_administration(request):
    return layout.render(request, 'admin/attribution_administration.html')


@login_required
@permission_required('base.is_faculty_administrator', raise_exception=True)
def select_tutor_attributions(request):
    if request.method == "POST":
        form = GlobalIdForm(request.POST)
        if form.is_valid():
            global_id = form.cleaned_data['global_id']
            return visualize_tutor_attributions(request, global_id)
    else:
        form = GlobalIdForm()
    return layout.render(request, "admin/attribution_administration.html", {"form": form})


@login_required
@permission_required('base.is_faculty_administrator', raise_exception=True)
def visualize_tutor_attributions(request, global_id):
    tutor = mdl_base.tutor.find_by_person_global_id(global_id)
    data = get_teaching_charge_data(tutor.person,  get_current_academic_year())
    return render(request, "tutor_charge.html", data)


def get_attributions_charge_duration(a_person, an_academic_year):
    attributions_charge_duration = {}
    try:
        server_top_url = settings.ATTRIBUTION_CONFIG.get('SERVER_TO_FETCH_URL')
        tutor_allocations_path = server_top_url + ATTRIBUTIONS_TUTOR_ALLOCATION_PATH
        url = tutor_allocations_path.format(global_id=a_person.global_id, year=an_academic_year.year)
        username = settings.ATTRIBUTION_CONFIG.get('SERVER_TO_FETCH_USER')
        password = settings.ATTRIBUTION_CONFIG.get('SERVER_TO_FETCH_PASSWORD')
        response = requests.get(url, auth=(username, password))
        if response.status_code == 200:
            tutor_allocations_json = response.json()
            attributions_charge_duration = _tutor_attributions_by_learning_unit(tutor_allocations_json)
    except Exception:
        attributions_charge_duration['error'] = True
    finally:
        return attributions_charge_duration


def _tutor_attributions_by_learning_unit(tutor_allocations_json):
    tutor_attributions = {}
    list_attributions = tutor_allocations_json.get("tutorAllocations", [])
    for attribution in list_attributions:
        if not attribution.get("allocationId") and not attribution.get('year'):
            continue
        attribution_external_id = \
            "osis.attribution_{attribution_id}".format(attribution_id=attribution['allocationId'])
        tutor_attributions[attribution_external_id] = {
            "lecturing_charge": attribution.get("allocationChargeLecturing", 0),
            "practical_charge": attribution.get("allocationChargePractical", 0),
            "learning_unit_charge": attribution.get("learningUnitCharge", 0)
        }
    return tutor_attributions
