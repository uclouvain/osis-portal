##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2021 Université catholique de Louvain (http://www.uclouvain.be)
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
import json
from operator import itemgetter
from typing import List, Dict

from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render

from attribution.business import xls_students_by_learning_unit
from attribution.services.enrollments import LearningUnitEnrollmentService
from attribution.services.learning_unit import LearningUnitService
from performance import models as mdl_performance

JSON_LEARNING_UNIT_NOTE = 'note'
JSON_LEARNING_UNIT_STATUS = 'etatExam'
JANUARY = "janvier"
JUNE = "juin"
SEPTEMBER = "septembre"


@login_required
@permission_required('base.is_faculty_administrator', raise_exception=True)
def show_students_admin(request, learning_unit_acronym, learning_unit_year):
    return render(request, "students_list_admin.html", _load_students(
        learning_unit_acronym, learning_unit_year, request.user
    ))


@login_required
@permission_required('base.can_access_attribution', raise_exception=True)
def show_students(request, learning_unit_acronym, learning_unit_year):
    return render(request, "students_list.html", _load_students(
        learning_unit_acronym, learning_unit_year, request.user
    ))


@login_required
@permission_required('base.can_access_attribution', raise_exception=True)
def students_list_build_by_learning_unit(request, learning_unit_acronym, learning_unit_year):
    a_learning_unit_yr = LearningUnitService.get_learning_unit(
        acronym=learning_unit_acronym,
        year=learning_unit_year,
        person=request.user.person
    )
    student_list = _get_learning_unit_yr_enrollments_list(a_learning_unit_yr, request.user)
    return xls_students_by_learning_unit.get_xls(student_list, a_learning_unit_yr)


def _load_students(learning_unit_acronym, learning_unit_year, user):
    a_learning_unit_year = LearningUnitService.get_learning_unit(
        acronym=learning_unit_acronym,
        year=learning_unit_year,
        person=user.person
    )
    students = _get_learning_unit_yr_enrollments_list(a_learning_unit_year, user)
    return {
        'global_id': user.person.global_id,
        'students': students,
        'learning_unit_year': a_learning_unit_year,
        'has_peps': _has_peps_student(students),
    }


def get_sessions_results(a_registration_id, a_learning_unit_year, offer_acronym):
    results = {}
    academic_year = a_learning_unit_year.academic_year
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
                _manage_cours_list(a_learning_unit_year, cours_list, results)
    return results


def _manage_cours_list(a_learning_unit_year, cours_list, results):
    if cours_list:
        nb_cours = 0
        while nb_cours < len(cours_list):
            cours = cours_list[nb_cours]
            if cours['sigleComplet'] == a_learning_unit_year.acronym:
                get_student_results(cours, results)
            nb_cours = nb_cours + 1


def get_student_results(cours, results):
    sessions = cours['session']
    nb_session = 0
    while nb_session < len(sessions):
        results.update({
            sessions[nb_session]['mois']: {
                JSON_LEARNING_UNIT_NOTE: get_value(sessions[nb_session], JSON_LEARNING_UNIT_NOTE),
                JSON_LEARNING_UNIT_STATUS: get_value(sessions[nb_session], JSON_LEARNING_UNIT_STATUS)
            }
        })
        nb_session = nb_session + 1


def get_student_data_dict(a_student_performance):
    try:
        data_input = json.dumps(a_student_performance.data)
        return json.loads(data_input)
    except (AttributeError, ValueError):
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


def get_enrollments_dict_for_display(learning_unit_enrollment, learning_unit_year):
    session_results = get_sessions_results(
        learning_unit_enrollment.student_registration_id,
        learning_unit_year,
        learning_unit_enrollment.program
    )

    student_specific_profile = learning_unit_enrollment.specific_profile

    return {
        'name': "{0}, {1}".format(
            learning_unit_enrollment.student_first_name,
            learning_unit_enrollment.student_last_name
        ),
        'email': learning_unit_enrollment.student_email,
        'program': learning_unit_enrollment.program,
        'acronym': learning_unit_enrollment.learning_unit_acronym,
        'registration_id': learning_unit_enrollment.student_registration_id,
        'january_note': get_session_value(session_results, JANUARY, JSON_LEARNING_UNIT_NOTE),
        'january_status': get_session_value(session_results, JANUARY, JSON_LEARNING_UNIT_STATUS),
        'june_note': get_session_value(session_results, JUNE, JSON_LEARNING_UNIT_NOTE),
        'june_status': get_session_value(session_results, JUNE, JSON_LEARNING_UNIT_STATUS),
        'september_note': get_session_value(session_results, SEPTEMBER, JSON_LEARNING_UNIT_NOTE),
        'september_status': get_session_value(session_results, SEPTEMBER, JSON_LEARNING_UNIT_STATUS),
        'student_specific_profile': student_specific_profile
    }


def _get_learning_unit_yr_enrollments_list(a_learning_unit_year, user) -> List[Dict]:
    enrollments_list = LearningUnitEnrollmentService.get_enrollments_list(
        year=a_learning_unit_year.academic_year,
        acronym=a_learning_unit_year.acronym,
        person=user.person
    )
    enrollments = [
        get_enrollments_dict_for_display(enrollment, a_learning_unit_year)
        for enrollment in enrollments_list
    ]
    return sorted(enrollments, key=itemgetter('program'))


def _has_peps_student(students):
    for enrollment in students:
        if enrollment.get('type_peps'):
            return True
    return False

