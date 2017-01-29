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
from django.core.exceptions import PermissionDenied

from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required, permission_required
from base.models import student
from performance import models as mdl_performance
from performance.forms import RegistrationIdForm
from base.views import layout
import json


@login_required
@permission_required('base.is_student', raise_exception=True)
def view_performance_home(request):
    """
    Display the academic programs of the student.
    """
    stud = student.find_by_user(request.user)
    list_student_programs = None
    if stud:
        list_student_programs = get_student_programs_list(stud)
    return layout.render(request, "performance_home.html", {"student": stud,
                                                            "programs": list_student_programs})


@login_required
@permission_required('base.is_student', raise_exception=True)
def display_result_for_specific_student_performance(request, pk):
    """
    Display the student result for a particular year and program.
    """
    stud = student.find_by_user(request.user)
    stud_perf = mdl_performance.student_performance.find_actual_by_pk(pk)
    if not check_right_access(stud_perf, stud):
        raise PermissionDenied
    document = json.dumps(stud_perf.data) if stud_perf else None
    creation_date = stud_perf.creation_date if stud_perf else None
    update_date = stud_perf.update_date if stud_perf else None
    fetch_timed_out = stud_perf.fetch_timed_out if stud_perf else None

    return layout.render(request, "performance_result.html", {"results": document,
                                                              "creation_date": creation_date,
                                                              "update_date": update_date,
                                                              "fetch_timed_out": fetch_timed_out})


@login_required
@permission_required('base.is_faculty_administrator', raise_exception=True)
def performance_administration(request):
    return layout.render(request, 'admin/performance_administration.html')


@login_required
@permission_required('base.is_faculty_administrator', raise_exception=True)
def select_student(request):
    """
    View to select a student to visualize his/her results.
    !!! Should only be accessible for staff having the rights.
    """
    if request.method == "POST":
        form = RegistrationIdForm(request.POST)
        if form.is_valid():
            registration_id = form.cleaned_data['registration_id']
            return redirect(visualize_student_programs, registration_id=registration_id)
    else:
        form = RegistrationIdForm()
    return layout.render(request, "admin/performance_select_student.html", {"form": form})


@login_required
@permission_required('base.is_faculty_administrator', raise_exception=True)
def visualize_student_programs(request, registration_id):
    """
    View to visualize a particular student list of academic programs.
    !!! Should only be accessible for staff having the rights.
    """
    stud = student.find_by_registration_id(registration_id)
    list_student_programs = None
    if stud:
        list_student_programs = get_student_programs_list(stud)

    return layout.render(request, "performance_home.html", {"student": stud,
                                                            "programs": list_student_programs})


@login_required
@permission_required('base.is_faculty_administrator', raise_exception=True)
def visualize_student_result(request, pk):
    """
    View to visualize a particular student program courses result.
    !!! Should only be accessible for staff having the rights.
    """
    stud_perf = mdl_performance.student_performance.find_actual_by_pk(pk)
    document = json.dumps(stud_perf.data) if stud_perf else None
    creation_date = stud_perf.creation_date if stud_perf else None
    update_date = stud_perf.update_date if stud_perf else None
    fetch_timed_out = stud_perf.fetch_timed_out if stud_perf else None

    return layout.render(request, "performance_result.html", {"results": document,
                                                              "creation_date": creation_date,
                                                              "update_date": update_date,
                                                              "fetch_timed_out": fetch_timed_out})


# *************************** UTILITY FUNCTIONS

def get_student_programs_list(stud):
    query_result = mdl_performance.student_performance.search(registration_id=stud.registration_id)
    list_student_programs = query_result_to_list(query_result)
    return list_student_programs


def query_result_to_list(query_result):
    l = []
    for row in query_result:
        d = convert_student_performance_to_dic(row)
        l.append(d)
    return l


def convert_student_performance_to_dic(student_performance_obj):
    d = dict()
    d["academic_year"] = student_performance_obj.academic_year
    d["acronym"] = student_performance_obj.acronym
    d["title"] = json.loads(json.dumps(student_performance_obj.data))["monAnnee"]["monOffre"]["offre"]["intituleComplet"]
    d["pk"] = student_performance_obj.pk
    return d


def check_right_access(student_performance, student):
    return student_performance.registration_id == student.registration_id


