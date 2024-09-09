# -*- coding: utf-8 -*-
############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2022 Université catholique de Louvain (http://www.uclouvain.be)
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
import logging
from datetime import datetime

from django.conf import settings
from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import PermissionDenied, MultipleObjectsReturned
from django.http import HttpRequest
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.translation import ugettext as _

import dashboard.views.home
from base.business import student as student_bsn
from base.forms.base_forms import RegistrationIdForm
from base.models import academic_year
from base.models.student import Student
from base.views import layout, common
from exam_enrollment.views.utils import get_request_timeout, get_exam_enroll_request
from performance import models as mdl_performance
from performance.models.student_performance import StudentPerformance

logger = logging.getLogger(settings.DEFAULT_LOGGER)


def __make_not_authorized_message(stud_perf):
    authorized = stud_perf.authorized if stud_perf else None
    session_month = stud_perf.get_session_locked_display() if stud_perf else None
    if not authorized and session_month:
        not_autorized_status = json.loads(json.dumps(stud_perf.data)).get('blockingType')
        if not_autorized_status and 'VERROU_SOLDE' == not_autorized_status:
            return _('The publication of the notes from the %(session_month)s session is not authorized '
                     'because, unless there is an error, there is still a balance of '
                     'your registration fees to be paid.<br/><br/>If you have paid very recently, '
                     'given the technical and banking delays, your situation may not yet have been updated. '
                     'In this case, your notes will be available the day after the regularization of your file. '
                     'If you have any questions about your debt to the university, please contact '
                     'the <a href=\"%(accounting_enrollment_service_url)s\" target=\"_blank\">Accounting Department '
                     'of the Enrollment Service</a>') % {
                "session_month": session_month,
                "accounting_enrollment_service_url": settings.REGISTRATION_ACCOUNT_SERVICE_URL
            }
        else:
            notes_diffusion_date = stud_perf.data.get('dateDiffusion')
            message = _('The publication of the notes from the %(session_month)s session was not authorized by our '
                        'faculty.') % {"session_month": session_month}
            if notes_diffusion_date and "VERROU_FACULTE" == not_autorized_status:
                # Le timestamp donné fourni par Java est en milisecondes et en python c'est en seconde.Donc il faut
                # diviser par 1000 avant la conversion
                diffusion_date = notes_diffusion_date/1000
                message = "{} {}".format(
                    message,
                    _('The publication of the notes is scheduled for the %(diffusion_date)s at %(diffusion_time)s') %
                    {
                        "diffusion_date": datetime.fromtimestamp(diffusion_date).strftime('%d-%m-%Y'),
                        "diffusion_time": datetime.fromtimestamp(diffusion_date).strftime('%H:%M'),
                    }
                )
            return message
    else:
        return None


def __get_performance_data(stud_perf, stud):
    document = json.dumps(stud_perf.data) if stud_perf else None
    creation_date = stud_perf.creation_date if stud_perf else None
    update_date = stud_perf.update_date if stud_perf else None
    fetch_timed_out = stud_perf.fetch_timed_out if stud_perf else None
    not_authorized_message = __make_not_authorized_message(stud_perf)
    courses_registration_validated = stud_perf.courses_registration_validated if stud_perf else None
    learning_units_outside_catalog = stud_perf.learning_units_outside_catalog if stud_perf else None
    course_registration_message = stud_perf.course_registration_message if stud_perf else None
    on_site_exams_info = stud_perf.on_site_exams_info \
        if stud_perf and stud_perf.on_site_exams_info else None
    return {
        "results": document,
        "creation_date": creation_date,
        "update_date": update_date,
        "fetch_timed_out": fetch_timed_out,
        "not_authorized_message": not_authorized_message,
        "courses_registration_validated": courses_registration_validated,
        "learning_units_outside_catalog": learning_units_outside_catalog,
        "course_registration_message": course_registration_message,
        "on_site_exams_info": on_site_exams_info,
        "covid_period": _get_covid_period(stud, stud_perf),
        "activiteAideReussite": _get_activite_aide_reussite(stud, stud_perf),
        "allegement_150_en_remediation": _get_allegement_150_en_remediation(stud_perf),
        "current_academic_year": academic_year.current_academic_year().year == stud_perf.academic_year
        if stud_perf else False
    }


@login_required
@permission_required('base.is_student', raise_exception=True)
def display_result_for_specific_student_performance(request, pk):
    """
    Display the student result for a particular year and program.
    """
    try:
        stud = student_bsn.find_by_user_and_discriminate(request.user)
    except MultipleObjectsReturned:
        return dashboard.views.home.show_multiple_registration_id_error(request)
    stud_perf = mdl_performance.student_performance.find_actual_by_pk(pk)
    if not check_right_access(stud_perf, stud):
        raise PermissionDenied

    perf_data = __get_performance_data(stud_perf, stud)
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
        stud = student_bsn.find_by_user_and_discriminate(request.user)
    except MultipleObjectsReturned:
        return dashboard.views.home.show_multiple_registration_id_error(request)
    cleaned_acronym = _clean_acronym(acronym)
    stud_perf = mdl_performance.student_performance.find_actual_by_student_and_offer_year(stud.registration_id,
                                                                                          academic_year,
                                                                                          cleaned_acronym)
    if not check_right_access(stud_perf, stud):
        raise PermissionDenied
    perf_data = __get_performance_data(stud_perf, stud)

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
    if not _can_access_performance_administration(request):
        raise PermissionDenied
    if request.method == "POST":
        form = RegistrationIdForm(request.POST)
        if form.is_valid():
            registration_id = form.cleaned_data['registration_id']
            return redirect(reverse('performance_student_programs_admin', kwargs={'registration_id': registration_id}))
    else:
        form = RegistrationIdForm()
    return layout.render(request, "admin/performance_administration.html", {"form": form})


@login_required
def visualize_student_result(request, pk):
    """
    View to visualize a particular student program courses result.
    !!! Should only be accessible for staff having the rights.
    """
    if not _can_access_performance_administration(request):
        raise PermissionDenied
    stud_perf = mdl_performance.student_performance.find_actual_by_pk(pk)
    if stud_perf and not __can_visualize_student_result(request, pk):
        raise PermissionDenied
    try:
        # Ici on est dans une vue d'administration où le gestionnaire accède aux différentes pages après avoir renseigné
        # le NOMA d'un étudiant
        # Comment ici cela pourrait-il fonctionner? L'utilisateur est un gestionnaire !!
        stud = student_bsn.find_by_user_and_discriminate(request.user)
    except MultipleObjectsReturned:
        return dashboard.views.home.show_multiple_registration_id_error(request)
    perf_data = __get_performance_data(stud_perf, stud)
    return layout.render(request,
                         "admin/performance_result_admin.html",
                         perf_data)


def check_right_access(student_performance, student):
    return student_performance and student and student_performance.registration_id == student.registration_id


def __can_visualize_student_result(request, performance_result_pk):
    """
    Student cannot access administration
    User can visualize the student result if :
        - The user is faculty_administrator
        - The user is program manager of the requested program
    """
    if request.user.has_perm('base.is_faculty_administrator'):
        return True
    if request.user.has_perm('base.is_student'):
        return False
    student_performance = mdl_performance.student_performance.find_actual_by_pk(performance_result_pk)
    if student_performance:
        managed_programs = common.get_managed_programs(request.user)
        return student_performance.acronym in managed_programs
    return False


def _can_access_performance_administration(request: HttpRequest) -> bool:
    """
    Student cannot access administration
    User can access performance results administration if :
        - The user is faculty_administrator
        - The user is program manager of at least one program
    """
    return request.user.has_perm('base.is_faculty_administrator') or (
            not request.user.has_perm('base.is_student') and bool(common.get_managed_programs(request.user))
    )


def _get_covid_period(student: Student, stud_perf: StudentPerformance) -> bool:
    if student:
        data = stud_perf.data
        offer = data.get('monAnnee', {}).get('monOffre', {}).get('offre')
        if offer:
            request_timeout = get_request_timeout()
            exam_enroll_request = get_exam_enroll_request(offer.get('sigleComplet'), request_timeout, student)
            if exam_enroll_request:
                try:
                    data = json.loads(exam_enroll_request.document)
                    return data.get('covid_period')
                except json.JSONDecodeError:
                    logger.exception("Json data is not valid")
    return False


def _get_activite_aide_reussite(student: Student, stud_perf: StudentPerformance) -> str:
    if student:
        return stud_perf.data.get('activiteAideReussite')


def _get_allegement_150_en_remediation(stud_perf: StudentPerformance) -> bool:
    if stud_perf:
        allegement150 = stud_perf.data.get('allegement150', 'NON')
        reorientation = stud_perf.data.get('reorientation', 'NON')
        if allegement150.upper() == 'OUI' and reorientation.upper() == 'NON':
            return True
    return False
