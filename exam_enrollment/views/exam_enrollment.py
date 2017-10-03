##############################################################################
#
# OSIS stands for Open Student Information System. It's an application
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
##############################################################################
import datetime
import json
import logging
import pika
import pika.exceptions
import traceback
from voluptuous import error as voluptuous_error
from django.conf import settings
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponse, Http404
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.http import require_GET
from django.core.exceptions import PermissionDenied, MultipleObjectsReturned
from base import models as mdl_base
from base.forms.base_forms import GlobalIdForm
from base.views import layout
from osis_common.document import paper_sheet
from osis_common.decorators.ajax import ajax_required
import assessments.models
from exam_enrollment.models import exam_enrollment_request
from django.db import connection
from django.db.utils import OperationalError as DjangoOperationalError, InterfaceError as DjangoInterfaceError
from psycopg2._psycopg import OperationalError as PsycopOperationalError, InterfaceError as  PsycopInterfaceError
import time
from django.contrib import messages
from django.http import response
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


logger = logging.getLogger(settings.DEFAULT_LOGGER)
queue_exception_logger = logging.getLogger(settings.QUEUE_EXCEPTION_LOGGER)


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
        return [enrol.offer_year for enrol in list(
            mdl_base.offer_enrollment.find_by_student_academic_year(stud, acad_year))]
    return None


def _get_exam_enrollment_form(off_year, request, stud):
    learn_unit_enrols = mdl_base.learning_unit_enrollment.find_by_student_and_offer_year(stud, off_year)
    if not learn_unit_enrols:
        messages.add_message(request, messages.WARNING, _('no_learning_unit_enrollment_found').format(off_year.acronym))
        return response.HttpResponseRedirect(reverse('dashboard_home'))
    offer_enrollments = mdl_base.offer_enrollment.find_by_student(stud)
    data = exam_enrollment_request.find_by_offer_enrollment(offer_enrollments)
    if data:
        data = json.loads(data.document)
        return layout.render(request, 'exam_enrollment_form.html', {'exam_enrollments': data.get('exam_enrollments'),
                                                                    'student': stud,
                                                                    'current_number_session': "",
                                                                    'academic_year': mdl_base.academic_year.current_academic_year(),
                                                                    'program': mdl_base.offer_year.find_by_id(off_year.id)})
    else:
        ask_exam_enrollment_form(stud, off_year)
        return layout.render(request, 'exam_enrollment_form.html', {'exam_enrollments': "",
                                                                    'student': stud,
                                                                    'current_number_session': "",
                                                                    'academic_year': mdl_base.academic_year.current_academic_year(),
                                                                    'program': mdl_base.offer_year.find_by_id(off_year.id)})


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


def check_exam_enrollment_form(request):
    student = mdl_base.student.find_by_user(request.user)
    if 'exam_enrollment' in settings.INSTALLED_APPS:
        if _check_offer_enrollments_in_db(student):
            return HttpResponse(status=200)
        else:
            return HttpResponse(status=404)
    return HttpResponse(status=405)


def _check_offer_enrollments_in_db(student):
    offer_enrollment = mdl_base.offer_enrollment.find_by_student(student)
    if offer_enrollment:
        offer_enrollment_in_db_and_uptodate = check_db_offer_enrollments(offer_enrollment)
    else:
        offer_enrollment_in_db_and_uptodate = False
        logger.warning("This person doesn't exist")
    return offer_enrollment_in_db_and_uptodate


def check_db_offer_enrollments(offer_enrollment):
    exam_enrollment = exam_enrollment_request.find_by_offer_enrollment(offer_enrollment)
    if not exam_enrollment or not exam_enrollment.document:
        return False
    else:
        return True


def get_data_schema():
    return Schema({
        Required("exam_enrollments"): str,
    }, extra=True)


def validate_data_structure(data):
    s = get_data_schema()
    return s(data)


def _fetch_exam_enrollment_form(stud, offer_yr):
    json_data = call_exam_enrollment_client(offer_yr, stud)
    if json_data:
        json_data = json_data.decode("utf-8")
        try:
            return json.loads(json_data)
        except ValueError:
            return None
    return None


def _process_exam_enrollment_form_submission(off_year, request, stud):
    data_to_submit = _exam_enrollment_form_submission_message(off_year, request, stud)
    json_data = json.dumps(data_to_submit)
    offer_enrol = offer_enrollment.find_by_student_offer(stud, off_year)
    if json_data and offer_enrol:
        exam_enrollment_submitted.insert_or_update_document(offer_enrol, json_data)
    queue_sender.send_message(settings.QUEUES.get('QUEUES_NAME').get('EXAM_ENROLLMENT_FORM_SUBMISSION'), data_to_submit)
    messages.add_message(request, messages.SUCCESS, _('exam_enrollment_form_submitted'))
    return response.HttpResponseRedirect(reverse('dashboard_home'))