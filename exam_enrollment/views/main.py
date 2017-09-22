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
import json

from django.core.exceptions import MultipleObjectsReturned
import warnings
from django.contrib.auth.decorators import login_required, permission_required
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from django.http import response
from django.conf import settings

from base.views import layout
from base.models import student, offer_enrollment, academic_year, offer_year, learning_unit_enrollment
from exam_enrollment.models import exam_enrollment_submitted
from frontoffice.queue import queue_listener
from osis_common.queue import queue_sender
from dashboard.views import main as dash_main_view


@login_required
@permission_required('base.is_student', raise_exception=True)
def choose_offer(request):
    return navigation(request, False)


@login_required
@permission_required('base.is_student', raise_exception=True)
def choose_offer_direct(request):
    return navigation(request, True)


def navigation(request, navigate_direct_to_form):
    try:
        stud = student.find_by_user(request.user)
    except MultipleObjectsReturned:
        return dash_main_view.show_multiple_registration_id_error(request)
    current_academic_year = academic_year.starting_academic_year()
    student_programs = _get_student_programs(stud, current_academic_year)
    if student_programs:
        if navigate_direct_to_form and len(student_programs) == 1:
            return _get_exam_enrollment_form(student_programs[0], request, stud)
        else:
            return layout.render(request, 'offer_choice.html', {'programs': student_programs,
                                                                'student': stud})
    else:
        messages.add_message(request, messages.WARNING, _('no_offer_enrollment_found').format(current_academic_year))
        return response.HttpResponseRedirect(reverse('dashboard_home'))


@login_required
@permission_required('base.is_student', raise_exception=True)
def exam_enrollment_form(request, offer_year_id):
    try:
        stud = student.find_by_user(request.user)
    except MultipleObjectsReturned:
        return dash_main_view.show_multiple_registration_id_error(request)
    off_year = offer_year.find_by_id(offer_year_id)
    if request.method == 'POST':
        return _process_exam_enrollment_form_submission(off_year, request, stud)
    else:
        return _get_exam_enrollment_form(off_year, request, stud)


def _get_exam_enrollment_form(off_year, request, stud):
    learn_unit_enrols = learning_unit_enrollment.find_by_student_and_offer_year(stud, off_year)
    if not learn_unit_enrols:
        messages.add_message(request, messages.WARNING, _('no_learning_unit_enrollment_found').format(off_year.acronym))
        return response.HttpResponseRedirect(reverse('dashboard_home'))
    data = _fetch_exam_enrollment_form(stud, off_year)
    if not data:
        messages.add_message(request, messages.WARNING, _('exam_enrollment_form_unavalaible_for_the_moment').format(off_year.acronym))
        return response.HttpResponseRedirect(reverse('dashboard_home'))
    elif data.get('error_message'):
        messages.add_message(request, messages.WARNING, _(data.get('error_message')).format(off_year.acronym))
        return response.HttpResponseRedirect(reverse('dashboard_home'))
    return layout.render(request, 'exam_enrollment_form.html', {'exam_enrollments': data.get('exam_enrollments'),
                                                                'student': stud,
                                                                'current_number_session': data.get('current_number_session'),
                                                                'academic_year': academic_year.current_academic_year(),
                                                                'program': offer_year.find_by_id(off_year.id)})


def _process_exam_enrollment_form_submission(off_year, request, stud):
    data_to_submit = _exam_enrollment_form_submission_message(off_year, request, stud)
    json_data = json.dumps(data_to_submit)
    offer_enrol = offer_enrollment.find_by_student_offer(stud, off_year)
    if json_data and offer_enrol:
        exam_enrollment_submitted.insert_or_update_document(offer_enrol, json_data)
    queue_sender.send_message(settings.QUEUES.get('QUEUES_NAME').get('EXAM_ENROLLMENT_FORM_SUBMISSION'), data_to_submit)
    messages.add_message(request, messages.SUCCESS, _('exam_enrollment_form_submitted'))
    return response.HttpResponseRedirect(reverse('dashboard_home'))


def _exam_enrollment_form_submission_message(off_year, request, stud):
    return {
        'registration_id': stud.registration_id,
        'offer_year_acronym': off_year.acronym,
        'year': off_year.academic_year.year,
        'exam_enrollments': _build_enrollments_by_learning_unit(request)
    }


def _build_enrollments_by_learning_unit(request):
    warnings.warn(
        "The field named 'etat_to_inscr' is only used to call EPC services. It should be deleted when the exam "
        "enrollment business will be implemented in Osis (not in EPC anymore). "
        "The flag 'is_enrolled' should be sufficient for Osis."
        "Do not forget to delete the hidden input field in the html template.",
        DeprecationWarning
    )
    current_number_session = request.POST['current_number_session']
    enrollments_by_learn_unit = []
    is_enrolled_by_acronym = _build_dicts_is_enrolled_by_acronym(current_number_session, request)
    etat_to_inscr_by_acronym = _build_dicts_etat_to_inscr_by_acronym(request)
    for acronym, etat_to_inscr in etat_to_inscr_by_acronym.items():
        etat_to_inscr = None if not etat_to_inscr or etat_to_inscr == 'None' else etat_to_inscr
        if etat_to_inscr:
            enrollments_by_learn_unit.append({
                'acronym': acronym,
                'is_enrolled': is_enrolled_by_acronym.get(acronym, False),
                'etat_to_inscr': etat_to_inscr
            })
    return enrollments_by_learn_unit


def _build_dicts_etat_to_inscr_by_acronym(request):
    return {_extract_acronym(html_tag_id): etat_to_inscr for html_tag_id, etat_to_inscr in request.POST.items()
            if "etat_to_inscr_current_session_" in html_tag_id}


def _build_dicts_is_enrolled_by_acronym(current_number_session, request):
    return {_extract_acronym(html_tag_id): True if value == "on" else False
            for html_tag_id, value in request.POST.items()
            if "chckbox_exam_enrol_sess{}_".format(current_number_session) in html_tag_id}


def _extract_acronym(html_tag_id):
    return html_tag_id.split("_")[-1]


def _fetch_exam_enrollment_form(stud, offer_yr):
    json_data = call_exam_enrollment_client(offer_yr, stud)
    if json_data:
        json_data = json_data.decode("utf-8")
        return json.loads(json_data)
    return None


def _exam_enrollment_form_message(registration_id, offer_year_acronym, year):
    return {
        'registration_id': registration_id,
        'offer_year_acronym': offer_year_acronym,
        'year': year,
    }


def _get_student_programs(stud, acad_year):
    if stud:
        return [enrol.offer_year for enrol in list(
            offer_enrollment.find_by_student_academic_year(stud, acad_year))]
    return None


def call_exam_enrollment_client(offer_yr, stud):
    if hasattr(settings, 'QUEUES') and settings.QUEUES:
        exam_enrol_client = queue_listener.ExamEnrollmentClient()
        message = _exam_enrollment_form_message(stud.registration_id, offer_yr.acronym, offer_yr.academic_year.year)
        return exam_enrol_client.call(json.dumps(message))
    return None
