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


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import ObjectDoesNotExist
from base.models.student import find_by_user, find_by_registration_id, Student
from base.models import offer_enrollment as mdl_offer_enrollment
from base.models import offer_year as mdl_offer_year
from performance import models as mdl_performance
from performance.forms import RegistrationIdForm
from base.views import layout


@login_required
@permission_required('base.is_student', raise_exception=True)
def home(request):
    """
    Display the academic programs of the student.
    """
    stud = find_by_user(request.user)
    list_student_programs = fetch_student_programs_list(stud)

    return layout.render(request, "performance_home.html", {"student": stud,
                                                     "programs": list_student_programs})


@login_required
@permission_required('base.is_faculty_administrator', raise_exception=True)
def performance_administration(request):
    return layout.render(request, 'admin/performance_administration.html')


@login_required
@permission_required('base.is_student', raise_exception=True)
def result_by_year_and_program(request, offer_year_id):
    """
    Display the student result for a particular year and program.
    """
    stud = find_by_user(request.user)
    offer_year = mdl_offer_year.find_by_id(offer_year_id)
    stud_perf = mdl_performance.student_performance.find_by_student_and_offer_year(student=stud, offer_year=offer_year)
    if stud_perf:
        document = stud_perf.data
    else:
        document = None
    return layout.render(request, "performance_result.html", {"results": document})


@login_required
@permission_required('base.is_faculty_administrator', raise_exception=True)
def select_student(request):
    """
    View to select a student to visualize his/her results.
    !!! Should only be open for staff having the rights.
    """
    if request.method == "POST":
        form = RegistrationIdForm(request.POST)
        if form.is_valid():
            registration_id = form.cleaned_data['registration_id']
            return redirect(student_programs, registration_id=registration_id)
    else:
        form = RegistrationIdForm()
    return layout.render(request, "admin/performance_select_student.html", {"form": form})


@login_required
@permission_required('base.is_faculty_administrator', raise_exception=True)
def student_programs(request, registration_id):
    """
    View to visualize a particular student list of academic programs.
    !!! Should only be open for staff having the rights.
    """
    stud = get_student_by_registration_id(registration_id)
    list_student_programs = fetch_student_programs_list(stud)

    return layout.render(request, "performance_home.html", {"student": stud,
                                                     "programs": list_student_programs})


@login_required
@permission_required('base.is_faculty_administrator', raise_exception=True)
def student_result(request, registration_id, anac, program_acronym):
    """
    View to visualize a particular student program courses result.
    !!! Should only be open for staff having the rights.
    """
    stud = get_student_by_registration_id(registration_id)

    query_result = mdl_performance.student_performance.select_where_registration_id_is(stud.registration_id)
    document = filter_by_anac_and_program_acronym(query_result, anac, program_acronym)

    return layout.render(request, "performance_result.html", {"results": document})


# *************************** UTILITY FUNCTIONS


def get_student_by_registration_id(registration_id):
    """
    Get the student having the corresponding registration_id.
    :param registration_id: a string
    :return: a student object or none
    """
    try:
        stud = find_by_registration_id(registration_id)
    except ObjectDoesNotExist:
        stud = None
    return stud


def fetch_student_programs_list(stud):
    """
    Fetch the student programs of the student "stud"
    :param stud: a student object
    :return: a list of dictionnary (see query_result_to_list for the format)
    """
    list_student_programs = None

    if stud:
        query_result = mdl_offer_enrollment.find_by_student(stud)
        list_student_programs = query_result_to_list(query_result)
    return list_student_programs


def query_result_to_list(query_result):
    """
    Parse the query result (a lisf of offer enrollments),
    to a list of dictonnary.
    :param query_result: a query result of offer_enrollments
    :return: a list of dictionaries
    """
    l = []
    for row in query_result:
        d = {}
        d["year"] =  row.offer_year.academic_year
        d["anac"] = row.offer_year.academic_year.year
        d["acronym"] = row.offer_year.acronym
        d["formatted_acronym"] = mdl_performance.student_performance.format_acronym(row.offer_year.acronym)
        d["title"] = row.offer_year.title
        d["program_id"] = row.offer_year.id
        l.append(d)
    return l


def filter_by_anac_and_program_acronym(query_result, anac, program_acronym):
    """
    Return the document which have anac equals to "anac" and program id
    equals to "program_id" from the query_results.
    :param query_result: a n1ql query object
    :param anac: a string
    :param program_acronym: a string
    :return: a json document
    """
    for row in query_result:
        academic_year = row["performance"]["academic_years"][0]
        program = academic_year["programs"][0]
        if academic_year["anac"] == anac and \
                        mdl_performance.student_performance.format_acronym(program["acronym"]) \
                        == mdl_performance.student_performance.format_acronym(program_acronym):
            return row["performance"]
    return None
