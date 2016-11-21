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


from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required, permission_required
from base.models.student import find_by_user, get_student_by_registration_id
from base.models import offer_enrollment as mdl_offer_enrollment
from base.models import offer_year as mdl_offer_year
from performance import models as mdl_performance
from performance.forms import RegistrationIdForm
from base.views import layout
import json


@login_required
@permission_required('base.is_student', raise_exception=True)
def display_performance_home(request):
    """
    Display the academic programs of the student.
    """
    stud = find_by_user(request.user)
    list_student_programs = None
    if stud:
        list_student_programs = get_student_programs_list(stud)
    return layout.render(request, "performance_home.html", {"student": stud,
                                                            "programs": list_student_programs})


@login_required
@permission_required('base.is_student', raise_exception=True)
def display_result_for_specific_year_and_program(request, offer_year_id):
    """
    Display the student result for a particular year and program.
    """
    stud = find_by_user(request.user)
    offer_year = mdl_offer_year.find_by_id(offer_year_id)
    stud_perf = mdl_performance.student_performance.find_or_fetch(student=stud, offer_year=offer_year)
    document = json.dumps(stud_perf.data) if stud_perf else None
    creation_date = stud_perf.creation_date if stud_perf else None

    return layout.render(request, "performance_result.html", {"results": document, "creation_date": creation_date})


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
    stud = get_student_by_registration_id(registration_id)
    list_student_programs = None
    if stud:
        list_student_programs = get_student_programs_list(stud)

    return layout.render(request, "performance_home.html", {"student": stud,
                                                            "programs": list_student_programs})


@login_required
@permission_required('base.is_faculty_administrator', raise_exception=True)
def visualize_student_result(request, registration_id, offer_year_id):
    """
    View to visualize a particular student program courses result.
    !!! Should only be accessible for staff having the rights.
    """
    stud = get_student_by_registration_id(registration_id)
    offer_year = mdl_offer_year.find_by_id(offer_year_id)
    stud_perf = mdl_performance.student_performance.find_or_fetch(student=stud, offer_year=offer_year)
    document = stud_perf.data if stud_perf else None

    return layout.render(request, "performance_result.html", {"results": document})


# *************************** UTILITY FUNCTIONS

def get_student_programs_list(stud):
    """
    Fetch the student programs of the student "stud"
    :param stud: a student object
    :return: a list of dictionnary (see query_result_to_list for the format)
    """
    query_result = mdl_offer_enrollment.find_by_student_ordered(stud)
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
        d = convert_offer_enrollment_to_dic(row)
        l.append(d)
    return l


def convert_offer_enrollment_to_dic(offer_enrollment_obj):
    d = dict()
    d["year"] = offer_enrollment_obj.offer_year.academic_year
    d["anac"] = offer_enrollment_obj.offer_year.academic_year.year
    d["acronym"] = offer_enrollment_obj.offer_year.acronym
    d["title"] = offer_enrollment_obj.offer_year.title
    d["program_id"] = offer_enrollment_obj.offer_year.id
    return d


