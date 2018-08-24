##############################################################################
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
from django.core.exceptions import PermissionDenied

from base import models as mdl_base
from base.forms.base_forms import GlobalIdForm
from base.views import layout
from osis_common.document import paper_sheet
from osis_common.decorators.ajax import ajax_required
import assessments.models

from django.db import connection
from django.db.utils import OperationalError as DjangoOperationalError, InterfaceError as DjangoInterfaceError
from psycopg2._psycopg import OperationalError as PsycopOperationalError, InterfaceError as  PsycopInterfaceError
import time

logger = logging.getLogger(settings.DEFAULT_LOGGER)
queue_exception_logger = logging.getLogger(settings.QUEUE_EXCEPTION_LOGGER)


@login_required
@permission_required('base.is_faculty_administrator', raise_exception=True)
def scores_sheets_admin(request):
    if request.method == "POST":
        form = GlobalIdForm(request.POST)
        if form.is_valid():
            global_id = form.cleaned_data['global_id']
            return tutor_scores_sheets(request, global_id)
    else:
        form = GlobalIdForm()
    return layout.render(request, "admin/scores_sheets.html", {"form": form})


@login_required
@permission_required('base.is_faculty_administrator', raise_exception=True)
def tutor_scores_sheets(request, global_id):
    person = mdl_base.person.find_by_global_id(global_id)
    scores_in_db_and_uptodate = _check_person_and_scores_in_db(person)
    if hasattr(settings, 'QUEUES') and settings.QUEUES:
        request_timeout = settings.QUEUES.get("QUEUES_TIMEOUT").get("PAPER_SHEET_TIMEOUT")
    else:
        request_timeout = settings.DEFAULT_QUEUE_TIMEOUT
    return layout.render(request, "scores_sheets.html", locals())


@login_required
@permission_required('base.is_tutor', raise_exception=True)
def score_encoding(request):
    score_encoding_url = settings.OSIS_SCORE_ENCODING_URL
    score_encoding_vpn_help_url = settings.OSIS_VPN_HELP_URL
    return layout.render(request, "score_encoding.html", locals())


@login_required
@permission_required('base.is_tutor', raise_exception=True)
def scores_sheets(request):
    person = mdl_base.person.find_by_user(request.user)
    scores_in_db_and_uptodate = _check_person_and_scores_in_db(person)
    if hasattr(settings, 'QUEUES') and settings.QUEUES:
        request_timeout = settings.QUEUES.get("QUEUES_TIMEOUT").get("PAPER_SHEET_TIMEOUT")
    else:
        request_timeout = settings.DEFAULT_QUEUE_TIMEOUT
    return layout.render(request, "scores_sheets.html", locals())


@login_required
@permission_required('base.is_tutor', raise_exception=True)
@require_GET
@ajax_required
def ask_papersheet(request, global_id):
    if 'assessments' in settings.INSTALLED_APPS:
        person = mdl_base.person.find_by_global_id(global_id)
        if hasattr(settings, 'QUEUES') and settings.QUEUES and person:
            try:
                message_published = ask_queue_for_papersheet(person)
            except (RuntimeError, pika.exceptions.ConnectionClosed, pika.exceptions.ChannelClosed,
                    pika.exceptions.AMQPError):
                return HttpResponse(status=400)

            if message_published:
                return HttpResponse(status=200)

    return HttpResponse(status=405)


def ask_queue_for_papersheet(person):
    connect = pika.BlockingConnection(_get_rabbit_settings())
    queue_name = settings.QUEUES.get('QUEUES_NAME').get('SCORE_ENCODING_PDF_REQUEST')
    channel = _create_channel(connect, queue_name)
    message_published = channel.basic_publish(exchange='',
                                              routing_key=queue_name,
                                              body=person.global_id)
    connect.close()
    return message_published


def insert_or_update_document_from_queue(body):
    try:
        json_data = body.decode("utf-8")
        data = json.loads(json_data)
        global_id = data.get('tutor_global_id')
        if global_id:
            assessments.models.score_encoding.insert_or_update_document(global_id, json_data)

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


@login_required
@permission_required('base.is_tutor', raise_exception=True)
@require_GET
@ajax_required
def check_papersheet(request, global_id):
    person = mdl_base.person.find_by_global_id(global_id)
    if 'assessments' in settings.INSTALLED_APPS:
        if _check_person_and_scores_in_db(person):
            return HttpResponse(status=200)
        else:
            return HttpResponse(status=404)
    return HttpResponse(status=405)


@login_required
@permission_required('base.is_tutor', raise_exception=True)
def download_papersheet(request, global_id=None):
    logged_person = mdl_base.person.find_by_user(request.user)
    searched_person = mdl_base.person.find_by_global_id(global_id)

    if logged_person == searched_person or request.user.has_perm('base.is_faculty_administrator'):
        person = searched_person
    else:
        raise PermissionDenied()

    if not person:
        raise Http404()

    pdf = print_scores(person.global_id)
    if pdf:
        filename = "%s.pdf" % _('scores_sheet')
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="%s"' % filename
        response.write(pdf)
        return response

    scores_sheets_unavailable = True
    return layout.render(request, "scores_sheets.html", locals())


def print_scores(global_id):
    json_document = get_score_sheet(global_id)
    if json_document:
        document = json.loads(json_document)
        try:
            paper_sheet.validate_data_structure(document)
            return paper_sheet.build_pdf(document)
        except (KeyError, voluptuous_error.Invalid):
            trace = traceback.format_exc()
            logger.error(trace)
            logger.warning("A document could not be produced from the json document of the global id {0}".format(global_id))
    else:
        logger.warning("A json document for the global id {0} doesn't exist.".format(global_id))
    return None


def get_score_sheet(global_id):
    scor_encoding = assessments.models.score_encoding.find_by_global_id(global_id)
    document = None
    if scor_encoding:
        document = scor_encoding.document
    try:
        if not document or is_outdated(document):
            return None
    except ValueError:
        return None

    return document


def check_db_scores(global_id):
    scores = assessments.models.score_encoding.find_by_global_id(global_id)
    if not scores or not scores.document:
        return False

    try:
        outdated_document = is_outdated(scores.document)
    except ValueError:
        return False

    if outdated_document:
        return False

    try:
        paper_sheet.validate_data_structure(json.loads(scores.document))
        return True
    except (KeyError, voluptuous_error.Invalid):
        trace = traceback.format_exc()
        logger.error(trace)
        logger.warning("A document could not be produced from the json document of the global id {0}".format(global_id))
        return False


def is_outdated(document):
    try:
        json_document = json.loads(document)
    except ValueError:
        trace = traceback.format_exc()
        logger.error(trace)
        logger.warning("The JSON document is invalid and cannot be loaded")
        raise

    now = datetime.datetime.now()
    now_str = '%s/%s/%s' % (now.day, now.month, now.year)
    if json_document.get('publication_date', None) != now_str:
            return True
    return False


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


def _check_person_and_scores_in_db(person):
    if person:
        scores_in_db_and_uptodate = check_db_scores(person.global_id)
    else:
        scores_in_db_and_uptodate = False
        logger.warning("This person doesn't exist")
    return scores_in_db_and_uptodate
