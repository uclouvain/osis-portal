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
from django.contrib.auth.decorators import login_required, user_passes_test, permission_required
from django.core.exceptions import ObjectDoesNotExist
from base.models.student import is_student, find_by_user, Student
from performance import models as mdl
from performance.forms import RegistrationIdForm


@login_required
@permission_required('base.is_student', raise_exception=True)
def home(request):
    """
    Display the academic programs of the student.
    """
    stud = find_by_user(request.user)
    list_student_programs = fetch_student_programs_list(stud)

    return render(request, "performance_home.html", {"student": stud,
                                                     "programs": list_student_programs})


@login_required
@user_passes_test(is_student)
def result_by_year_and_program(request, anac, program_acronym):
    """
    Display the student result for a particular year and program.
    """
    stud = find_by_user(request.user)
    query_result = mdl.student_performance.select_where_registration_id_is(stud.registration_id)
    document = filter_by_anac_and_program_acronym(query_result, anac, program_acronym)
    return render(request, "performance_result.html", {"results": document})


@login_required
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
    form = RegistrationIdForm()
    return render(request, "performance_select_student.html", {"form": form})


@login_required
def student_programs(request, registration_id):
    """
    View to visualize a particular student list of academic programs.
    """
    try:
        stud = Student.objects.get(registration_id=registration_id)
    except ObjectDoesNotExist:
        stud = None

    list_student_programs = fetch_student_programs_list(stud)

    return render(request, "performance_home.html", {"student": stud,
                                                     "programs": list_student_programs})


def fetch_student_programs_list(stud):
    """
    Fetch the student programs of the student "stud"
    :param stud: a student object
    :return: a list of dictionnary (see query_result_to_list for the format)
    """
    list_student_programs = None

    if stud:
        query_result = mdl.student_performance.select_where_registration_id_is(stud.registration_id)
        list_student_programs = query_result_to_list(query_result)
    return list_student_programs


def query_result_to_list(query_result):
    """
    Parse the query result (a select all on the bucket performance),
    to a list of dictonnary.
    :param query_result: a n1ql query object
    :return: a list of dictionaries
    """
    l = []
    for row in query_result:
        d = {}
        academic_year = row["performance"]["academic_years"][0]
        program = academic_year["programs"][0]
        d["year"] =  academic_year["year"]
        d["anac"] = academic_year["anac"]
        d["acronym"] = program["acronym"]
        d["formatted_acronym"] = mdl.student_performance.format_acronym(program["acronym"])
        d["title"] = program["title"]
        d["program_id"] = program["program_id"]
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
                        mdl.student_performance.format_acronym(program["acronym"]) \
                        == mdl.student_performance.format_acronym(program_acronym):
            return row["performance"]
    return None

