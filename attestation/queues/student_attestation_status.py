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
import json
import logging
from django.conf import settings
from frontoffice.queue.queue_listener import AttestationStatusClient

logger = logging.getLogger(settings.DEFAULT_LOGGER)


def fetch_json_attestation_statuses(message):
    attestation_statuses = None
    if message:
        try:
            client = AttestationStatusClient()
            json_data = client.call(message)
            if json_data:
                attestation_statuses = json.loads(json_data.decode("utf-8"))
        except Exception as e:
            logger.error('Error fetching student attestation statuses.\nmessage sent :  {}'.format(str(message)))
    return attestation_statuses
