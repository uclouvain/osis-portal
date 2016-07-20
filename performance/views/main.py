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

from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from base.models.student import is_student, find_by_user
from performance import models as mdl


@login_required
@user_passes_test(is_student)
def home(request):
    """
    Display the academic results of the student.
    """
    # Fetch the student academic results.
    stud = find_by_user(request.user)
    query_result = mdl.student_performance.select_where_global_id_is(stud.registration_id)
    list_student_programs = get_student_programs_list(query_result)
    return render(request, "performance_home.html", {"student": stud,
                                                     "programs": list_student_programs})

@login_required
@user_passes_test(is_student)
def result_by_year_and_program(request, anac, program_id):
    stud = find_by_user(request.user)
    query_result = mdl.student_performance.select_where_global_id_is(stud.registration_id)
    document = filter_by_anac_and_program_id(query_result, anac, program_id)
    return render(request, "performance_result.html", {"results": document})

def get_student_programs_list(query_result):
    """
    Get the list of programs for a student.
    This list contains info for each program which are:
    academic year and anac, program acronym, title and id.
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
        d["title"] = program["title"]
        d["program_id"] = program["program_id"]
        l.append(d)
    return l

def filter_by_anac_and_program_id(query_result, anac, program_id):
    """
    Return the document which have anac equals to "anac" and program id
    equals to "program_id"
    :param query_result: a n1ql query object
    :param anac: a string
    :param program_id: a string
    :return: a json document
    """
    for row in query_result:
        academic_year = row["performance"]["academic_years"][0]
        program = academic_year["programs"][0]
        if academic_year["anac"] == anac and program["program_id"] == program_id:
            return row["performance"]
    return None

