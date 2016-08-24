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
from couchbase.exceptions import ValueFormatError
from django.conf import settings
from osis_common.document import paper_sheet
from dashboard import models as mdl
from frontoffice.queue.queue import ScoresSheetClient
import datetime
import json
import logging


logger = logging.getLogger(settings.DEFAULT_LOGGER)


def get_score_sheet(global_id):
    logger.debug("Instanciating the QueueConnection ScoresSheetClient...")
    scores_sheets_cli = ScoresSheetClient()
    logger.debug("Done.")

    logger.debug("Sending the global id in the queue and waiting for a response...")
    json_data = scores_sheets_cli.call(global_id)
    logger.debug("Done.")
    logger.debug("Json.loads data consumed in the queue...")
    updated_document = json.loads(json_data.decode("utf-8"))
    logger.debug("Done.")
    try:
        logger.debug("Updating/inserting the document in Couchbase...")
        mdl.score_encoding.insert_or_update_document(global_id, updated_document)
        logger.debug("Done.")
    except ValueFormatError:
        logger.debug("Document already in couchbase and last updated today.")
        return None
    return updated_document


def print_scores(request, global_id):
    logger.debug("Searching document in couchbase (global id = " + global_id + ")")
    document = mdl.score_encoding.get_document(global_id)
    document = document.value if document else None
    if document:
        logger.debug("Document found")
        now = datetime.datetime.now()
        now_str = '%s/%s/%s' % (now.day, now.month, now.year)
        if document.get('publication_date', None) != now_str:
            document = get_score_sheet(global_id)
    else:
        logger.debug("No document found in couchbase")
        document = get_score_sheet(global_id)
    if document:
        logger.debug("Calling build_pdf() method to generate the pdf...")
        return paper_sheet.build_pdf(document)
    else:
        return None
