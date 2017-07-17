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
from django.http import HttpResponse
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.http import require_http_methods

from base import models as mdl_base
from base.views import layout
from osis_common.document import paper_sheet
import assessments.models

logger = logging.getLogger(settings.DEFAULT_LOGGER)
queue_exception_logger = logging.getLogger(settings.QUEUE_EXCEPTION_LOGGER)


@login_required
@permission_required('base.is_tutor', raise_exception=True)
def score_encoding(request):
    score_encoding_url = settings.OSIS_SCORE_ENCODING_URL
    score_encoding_vpn_help_url = settings.OSIS_SCORE_ENCODING_VPN_HELP_URL
    return layout.render(request, "score_encoding.html", locals())


@login_required
@permission_required('base.is_tutor', raise_exception=True)
def my_scores_sheets(request):
    scores_in_db_and_uptodate = _check_person_and_scores_in_db(request)
    return layout.render(request, "my_scores_sheets.html", locals())


@login_required
@permission_required('base.is_tutor', raise_exception=True)
@require_http_methods(["POST"])
def ask_papersheet(request):
    if request.is_ajax() and 'assessments' in settings.INSTALLED_APPS:
        person = mdl_base.person.find_by_user(request.user)
        if hasattr(settings, 'QUEUES') and settings.QUEUES:
            try:
                connect = pika.BlockingConnection(_get_rabbit_settings())
                queue_name = settings.QUEUES.get('QUEUES_NAME').get('SCORE_ENDCODING_PDF_REQUEST')
                channel = _create_channel(connect, queue_name)
                message_published = channel.basic_publish(exchange='',
                                                          routing_key=queue_name,
                                                          body=person.global_id)
                connect.close()
            except (RuntimeError, pika.exceptions.ConnectionClosed, pika.exceptions.ChannelClosed,
                    pika.exceptions.AMQPError):
                return HttpResponse(status=400)

            if message_published:
                return HttpResponse(status=200)

    return HttpResponse(status=405)


def insert_or_update_document_from_queue(body):
    json_data = body.decode("utf-8")
    data = json.loads(json_data)
    global_id = data.get('tutor_global_id')
    if global_id:
        assessments.models.score_encoding.insert_or_update_document(global_id, json_data)


@login_required
@permission_required('base.is_tutor', raise_exception=True)
@require_http_methods(["POST"])
def check_papersheet(request):
    if request.is_ajax() and 'assessments' in settings.INSTALLED_APPS:
        if _check_person_and_scores_in_db(request):
            return HttpResponse(status=200)
        else:
            return HttpResponse(status=404)
    else:
        return HttpResponse(status=405)


@login_required
@permission_required('base.is_tutor', raise_exception=True)
def download_papersheet(request):
    person = mdl_base.person.find_by_user(request.user)
    if person:
        pdf = print_scores(person.global_id)
        if pdf:
            filename = "%s.pdf" % _('scores_sheet')
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="%s"' % filename
            response.write(pdf)
            return response
    else:
        logger.warning("A person doesn't exist for the user {0}".format(request.user))

    scores_sheets_unavailable = True
    return layout.render(request, "my_scores_sheets.html", locals())


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
    if not document or is_outdated(document):
        return None
    return document


def check_db_scores(global_id):
    scores = assessments.models.score_encoding.find_by_global_id(global_id)
    if scores and scores.document and not is_outdated(scores.document):
        try:
            paper_sheet.validate_data_structure(json.loads(scores.document))
            return True
        except (KeyError, voluptuous_error.Invalid):
            trace = traceback.format_exc()
            logger.error(trace)
            logger.warning(
                "A document could not be produced from the json document of the global id {0}".format(global_id))
            return False
    else:
        return False


def is_outdated(document):
    json_document = json.loads(document)
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


def _check_person_and_scores_in_db(request):
    person = mdl_base.person.find_by_user(request.user)
    if person:
        scores_in_db_and_uptodate = check_db_scores(person.global_id)
    else:
        scores_in_db_and_uptodate = False
        logger.warning("A person doesn't exist for the user {0}".format(request.user))
    return scores_in_db_and_uptodate
