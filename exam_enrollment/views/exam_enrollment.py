##############################################################################
#
# OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2018 Université catholique de Louvain (http://www.uclouvain.be)
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
import logging
import time
import traceback
import warnings

import pika
import pika.exceptions
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import MultipleObjectsReturned
from django.core.urlresolvers import reverse
from django.db import connection
from django.db.utils import OperationalError as DjangoOperationalError, InterfaceError as DjangoInterfaceError
from django.http import HttpResponse, response
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from psycopg2._psycopg import OperationalError as PsycopOperationalError, InterfaceError as  PsycopInterfaceError

from base import models as mdl_base
from base.models import student, offer_enrollment, offer_year
from base.views import layout
from dashboard.views import main as dash_main_view
from exam_enrollment.models import exam_enrollment_request, exam_enrollment_submitted
from osis_common.queue import queue_sender

logger = logging.getLogger(settings.DEFAULT_LOGGER)
queue_exception_logger = logging.getLogger(settings.QUEUE_EXCEPTION_LOGGER)


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
        stud = mdl_base.student.find_by_user(request.user)
    except MultipleObjectsReturned:
        return dash_main_view.show_multiple_registration_id_error(request)
    current_academic_year = mdl_base.academic_year.starting_academic_year()
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


def _get_student_programs(stud, acad_year):
    if stud:
        return [
            enrol.offer_year for enrol in list(mdl_base.offer_enrollment.find_by_student_academic_year(stud, acad_year))
        ]
    return None


def _get_exam_enrollment_form(off_year, request, stud):
    learn_unit_enrols = mdl_base.learning_unit_enrollment.find_by_student_and_offer_year(stud, off_year)
    if not learn_unit_enrols:
        messages.add_message(request, messages.WARNING, _('no_learning_unit_enrollment_found').format(off_year.acronym))
        return response.HttpResponseRedirect(reverse('dashboard_home'))

    request_timeout = settings.QUEUES.get("QUEUES_TIMEOUT").get("EXAM_ENROLLMENT_FORM_RESPONSE")
    fetch_date_limit = timezone.now() - timezone.timedelta(seconds=request_timeout)
    exam_enroll_request = exam_enrollment_request.\
        get_by_student_and_offer_year_acronym_and_fetch_date(stud, off_year.acronym, fetch_date_limit)
    if exam_enroll_request:
        try:
            data = json.loads(exam_enroll_request.document)
        except json.JSONDecodeError:
            logger.exception("Json data is not valid")
            data = {}

        if data.get('error_message'):
            error_message = _(data.get('error_message')).format(off_year.acronym)
        else:
            error_message = data.get('error_message')

        return layout.render(request, 'exam_enrollment_form.html',
                             {'error_message': error_message,
                              'exam_enrollments': data.get('exam_enrollments'),
                              'student': stud,
                              'current_number_session': data.get('current_number_session'),
                              'academic_year': mdl_base.academic_year.current_academic_year(),
                              'program': mdl_base.offer_year.find_by_id(off_year.id),
                              'request_timeout': request_timeout})
    else:
        ask_exam_enrollment_form(stud, off_year)
        return layout.render(request, 'exam_enrollment_form.html',
                             {'exam_enrollments': "",
                              'student': stud,
                              'current_number_session': "",
                              'academic_year': mdl_base.academic_year.current_academic_year(),
                              'program': mdl_base.offer_year.find_by_id(off_year.id),
                              'request_timeout': request_timeout})


def ask_exam_enrollment_form(stud, off_year):
    if 'exam_enrollment' in settings.INSTALLED_APPS:
        if hasattr(settings, 'QUEUES') and settings.QUEUES:
            try:
                message_published = ask_queue_for_exam_enrollment_form(stud, off_year)
            except (RuntimeError, pika.exceptions.ConnectionClosed, pika.exceptions.ChannelClosed,
                    pika.exceptions.AMQPError):
                return HttpResponse(status=400)
            if message_published:
                return HttpResponse(status=200)
    return HttpResponse(status=405)


def ask_queue_for_exam_enrollment_form(stud, offer_yr):
    connect = pika.BlockingConnection(_get_rabbit_settings())
    queue_name = settings.QUEUES.get('QUEUES_NAME').get('EXAM_ENROLLMENT_FORM_REQUEST')
    channel = _create_channel(connect, queue_name)
    message = _exam_enrollment_form_message(stud.registration_id, offer_yr.acronym, offer_yr.academic_year.year)
    message_published = channel.basic_publish(exchange='',
                                              routing_key=queue_name,
                                              body=json.dumps(message))
    connect.close()
    return message_published


def _get_rabbit_settings():
    credentials = pika.PlainCredentials(settings.QUEUES.get('QUEUE_USER'),
                                        settings.QUEUES.get('QUEUE_PASSWORD'))
    rabbit_settings = pika.ConnectionParameters(settings.QUEUES.get('QUEUE_URL'),
                                                settings.QUEUES.get('QUEUE_PORT'),
                                                settings.QUEUES.get('QUEUE_CONTEXT_ROOT'),
                                                credentials)
    return rabbit_settings


def _create_channel(connect, queue_name):
    channel = connect.channel()
    channel.queue_declare(queue=queue_name, durable=True)
    return channel


def _exam_enrollment_form_message(registration_id, offer_year_acronym, year):
    return {
        'registration_id': registration_id,
        'offer_year_acronym': offer_year_acronym,
        'year': year,
    }


def check_exam_enrollment_form(request, offer_year_id):
    a_student = mdl_base.student.find_by_user(request.user)
    off_year = offer_year.find_by_id(offer_year_id)
    if 'exam_enrollment' in settings.INSTALLED_APPS:
        if _exam_enrollment_up_to_date_in_db_with_document(a_student, off_year):
            return HttpResponse(status=200)
        else:
            return HttpResponse(status=404)
    return HttpResponse(status=405)


def _exam_enrollment_up_to_date_in_db_with_document(a_student, off_year):
    an_offer_enrollment = mdl_base.offer_enrollment.get_by_student_offer(a_student, off_year)
    if an_offer_enrollment:
        request_timeout = settings.QUEUES.get("QUEUES_TIMEOUT").get("EXAM_ENROLLMENT_FORM_RESPONSE")
        fetch_date_limit = timezone.now() - timezone.timedelta(seconds=request_timeout)
        exam_enroll_request = exam_enrollment_request.\
            get_by_student_and_offer_year_acronym_and_fetch_date(a_student, off_year.acronym, fetch_date_limit)
        return exam_enroll_request and exam_enroll_request.document
    else:
        logger.warning("This student is not enrolled in this offer_year")
        return False


def _process_exam_enrollment_form_submission(off_year, request, stud):
    data_to_submit = _exam_enrollment_form_submission_message(off_year, request, stud)
    json_data = json.dumps(data_to_submit)
    offer_enrol = offer_enrollment.get_by_student_offer(stud, off_year)
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


def insert_or_update_document_from_queue(body):
    try:
        json_data = body.decode("utf-8")
        data = json.loads(json_data)
        registration_id = data.get('registration_id')
        acronym = data.get('offer_year_acronym')
        if registration_id:
            a_student = mdl_base.student.find_by_registration_id(registration_id)
            exam_enrollment_request.insert_or_update_document(acronym, a_student, json_data)
    except (PsycopOperationalError, PsycopInterfaceError, DjangoOperationalError, DjangoInterfaceError):
        queue_exception_logger.error('Postgres Error during insert_or_update_document_from_queue => retried')
        trace = traceback.format_exc()
        queue_exception_logger.error(trace)
        connection.close()
        time.sleep(1)
        insert_or_update_document_from_queue(body)
    except Exception:
        logger.warning('(Not PostgresError) during insert_or_update_document_from_queue')
        trace = traceback.format_exc()
        logger.error(trace)
