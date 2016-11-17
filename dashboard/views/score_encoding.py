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
from django.conf import settings
from osis_common.document import paper_sheet
from dashboard import models as mdl
from osis_common.queue.queue_listener import ScoresSheetClient
import datetime
import logging
import json


logger = logging.getLogger(settings.DEFAULT_LOGGER)


def get_score_sheet(global_id):
    document = mdl.score_encoding.get_document(global_id)
    if not document or is_outdated(document):
        document = fetch_document(global_id)
    return document


def fetch_document(global_id):
    json_data = fetch_json(global_id)
    if not json_data:
        return None
    return mdl.score_encoding.insert_or_update_document(global_id, json_data).document


def fetch_json(global_id):
    scores_sheets_cli = ScoresSheetClient()
    json_data = scores_sheets_cli.call(global_id)
    if json_data:
        json_data = json_data.decode("utf-8")
    return json_data


def is_outdated(document):
    json_document = json.loads(document)
    now = datetime.datetime.now()
    now_str = '%s/%s/%s' % (now.day, now.month, now.year)
    if json_document.get('publication_date', None) != now_str:
            return True
    return False


def print_scores(request, global_id):
    document = get_score_sheet(global_id)
    if document:
        document = json.loads(document)
        return paper_sheet.build_pdf(document)
    return None
