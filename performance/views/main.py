# -*- coding: utf-8 -*-
############################################################################
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
############################################################################
import json

from django.core.exceptions import PermissionDenied, MultipleObjectsReturned
from django.core.serializers.json import DjangoJSONEncoder
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.utils.translation import ugettext as _

from base.models import student, offer_enrollment
from performance import models as mdl_performance
from base.forms.base_forms import RegistrationIdForm
from base.views import layout, common
from performance.models.enums import offer_registration_state
from dashboard.views import main as dash_main_view


# Students Views

@login_required
@permission_required('base.is_student', raise_exception=True)
def view_performance_home(request):
    """
    Display the academic programs of the student.
    """
    try:
        stud = student.find_by_user(request.user)
    except MultipleObjectsReturned:
        return dash_main_view.show_multiple_registration_id_error(request)
    list_student_programs = None
    if stud:
        list_student_programs = get_student_programs_list(stud)
    data = {"student": stud,
            "programs": list_student_programs,
            "registration_states_to_show": offer_registration_state.STATES_TO_SHOW_ON_PAGE}
    return layout.render(request, "performance_home_student.html", data)


def __make_not_authorized_message(stud_perf):
    authorized = stud_perf.authorized if stud_perf else None
    session_month = stud_perf.get_session_locked_display() if stud_perf else None
    if not authorized and session_month:
        return _('The publication of the notes from the %(session_month)s session was not authorized by our faculty.')\
               % {"session_month": session_month}
    else:
        return None


def __get_performance_data(stud_perf):
    document = json.dumps(stud_perf.data) if stud_perf else None
    creation_date = stud_perf.creation_date if stud_perf else None
    update_date = stud_perf.update_date if stud_perf else None
    fetch_timed_out = stud_perf.fetch_timed_out if stud_perf else None
    not_authorized_message = __make_not_authorized_message(stud_perf)
    courses_registration_validated = stud_perf.courses_registration_validated if stud_perf else None
    learning_units_outside_catalog = stud_perf.learning_units_outside_catalog if stud_perf else None
    return {
        "results": document,
        "creation_date": creation_date,
        "update_date": update_date,
        "fetch_timed_out": fetch_timed_out,
        "not_authorized_message": not_authorized_message,
        "courses_registration_validated": courses_registration_validated,
        "learning_units_outside_catalog": learning_units_outside_catalog
    }


@login_required
@permission_required('base.is_student', raise_exception=True)
def display_result_for_specific_student_performance(request, pk):
    """
    Display the student result for a particular year and program.
    """
    try:
        stud = student.find_by_user(request.user)
    except MultipleObjectsReturned:
        return dash_main_view.show_multiple_registration_id_error(request)
    stud_perf = mdl_performance.student_performance.find_actual_by_pk(pk)
    if not check_right_access(stud_perf, stud):
        raise PermissionDenied

    perf_data = __get_performance_data(stud_perf)
    return layout.render(request,
                         "performance_result_student.html",
                         perf_data)


def _clean_acronym(acronym):
    if acronym:
        cleaned_acronym = str(acronym).replace("_", "/").upper()
        return cleaned_acronym
    return None


@login_required
@permission_required('base.is_student', raise_exception=True)
def display_results_by_acronym_and_year(request, acronym, academic_year):
    """
    Display the result for a students , filter by acronym
    """
    try:
        stud = student.find_by_user(request.user)
    except MultipleObjectsReturned:
        return dash_main_view.show_multiple_registration_id_error(request)
    cleaned_acronym = _clean_acronym(acronym)
    stud_perf = mdl_performance.student_performance.find_actual_by_student_and_offer_year(stud.registration_id,
                                                                                          academic_year,
                                                                                          cleaned_acronym)
    if not check_right_access(stud_perf, stud):
        raise PermissionDenied
    perf_data = __get_performance_data(stud_perf)

    return layout.render(request,
                         "performance_result_student.html",
                         perf_data)


# Admins Views

@login_required
def select_student(request):
    """
    View to select a student to visualize his/her results.
    !!! Should only be accessible for staff having the rights.
    """
    if not can_access_performance_administration(request):
        raise PermissionDenied
    if request.method == "POST":
        form = RegistrationIdForm(request.POST)
        if form.is_valid():
            registration_id = form.cleaned_data['registration_id']
            if not can_access_student_performance(request, registration_id):
                raise PermissionDenied
            return redirect(visualize_student_programs, registration_id=registration_id)
    else:
        form = RegistrationIdForm()
    return layout.render(request, "admin/performance_administration.html", {"form": form})


@login_required
def visualize_student_programs(request, registration_id):
    """
    View to visualize a particular student list of academic programs.
    !!! Should only be accessible for staff having the rights.
    """
    if not can_access_performance_administration(request) or \
            not can_access_student_performance(request, registration_id):
        raise PermissionDenied
    stud = student.find_by_registration_id(registration_id)
    list_student_programs = None
    if stud:
        list_student_programs = get_student_programs_list(stud)

    data = {"student": stud,
            "programs": list_student_programs,
            "registration_states_to_show": offer_registration_state.STATES_TO_SHOW_ON_PAGE}
    return layout.render(request, "admin/performance_home_admin.html", data)


@login_required
def visualize_student_result(request, pk):
    """
    View to visualize a particular student program courses result.
    !!! Should only be accessible for staff having the rights.
    """
    if not can_access_performance_administration(request):
        raise PermissionDenied
    stud_perf = mdl_performance.student_performance.find_actual_by_pk(pk)
    if stud_perf and not can_access_student_performance(request, stud_perf.registration_id, stud_perf):
        raise PermissionDenied
    perf_data = __get_performance_data(stud_perf)
    return layout.render(request,
                         "admin/performance_result_admin.html",
                         perf_data)


def get_student_programs_list(stud):
    query_result = mdl_performance.student_performance.search(registration_id=stud.registration_id)
    list_student_programs = query_result_to_list(query_result)
    return list_student_programs


def query_result_to_list(query_result):
    performance_results_list = []
    for row in query_result:
        performance_dict = convert_student_performance_to_dic(row)
        allowed_registration_states = [value for key, value in offer_registration_state.OFFER_REGISTRAION_STATES]
        if performance_dict and performance_dict.get("offer_registration_state") in allowed_registration_states:
            performance_results_list.append(performance_dict)
    return performance_results_list


def convert_student_performance_to_dic(student_performance_obj):
    d = dict()
    try:
        d["academic_year"] = student_performance_obj.academic_year_template_formated
        d["acronym"] = student_performance_obj.acronym
        d["title"] = json.loads(json.dumps(student_performance_obj.data))["monAnnee"]["monOffre"]["offre"]["intituleComplet"]
        d["pk"] = student_performance_obj.pk
        d["offer_registration_state"] = student_performance_obj.offer_registration_state
    except Exception:
        d = None
    return d


def check_right_access(student_performance, student):
    return student_performance and student and student_performance.registration_id == student.registration_id


def can_access_performance_administration(request):
    _set_managed_programs_if_not(request)
    is_fac_admin = request.user.has_perm('base.is_faculty_administrator')
    is_fac_manager = request.session.get('is_faculty_manager')
    return is_fac_admin or is_fac_manager


def can_access_student_performance(request, registration_id=None, stud_perf=None):
    _set_managed_programs_if_not(request)
    if request.user.has_perm('base.is_faculty_administrator'):
        return True
    if registration_id:
        user_managed_programs_in_session = request.session.get('managed_programs')
        if user_managed_programs_in_session:
            user_managed_programs = json.loads(user_managed_programs_in_session)
            if stud_perf:
                return stud_perf.acronym in user_managed_programs.get(str(stud_perf.academic_year), [])
            else:
                stud = student.find_by_registration_id(registration_id)
                if stud:
                    for stud_offer_enrollment in offer_enrollment.find_by_student(stud):
                        if stud_offer_enrollment.offer_year.acronym in user_managed_programs.get(
                                str(stud_offer_enrollment.offer_year.academic_year.year), []):
                            return True
    return False


def _set_managed_programs_if_not(request):
    if request.user.has_perm('base.is_student'):
        request.session['is_faculty_manager'] = False
        request.session['managed_programs'] = None
        request.session.save()
    if request.session.get('is_faculty_manager', None) is None:
        managed_programs_as_dict = common.get_managed_program_as_dict(request.user)
        if managed_programs_as_dict:
            request.session['is_faculty_manager'] = True
            managed_programs = json.dumps(managed_programs_as_dict, cls=DjangoJSONEncoder)
            request.session['managed_programs'] = managed_programs
            request.session.save()
