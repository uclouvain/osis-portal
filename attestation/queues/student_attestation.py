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
import urllib
from urllib.error import URLError
import logging

from django.conf import settings


logger = logging.getLogger(settings.DEFAULT_LOGGER)


def fetch_student_attestation(global_id, academic_year, attestation_type):
    server_top_url = settings.ATTESTATION_CONFIG.get('SERVER_TO_FETCH_URL')
    document_base_path = server_top_url + settings.ATTESTATION_CONFIG.get('ATTESTATION_PATH')
    if document_base_path:
        try:
            document_url = document_base_path.format(global_id=global_id,
                                                     academic_year=academic_year,
                                                     attestation_type=attestation_type)
            return _fetch_with_basic_auth(server_top_url, document_url)
        except URLError:
            logger.exception('Error when interacting with the attestation web services.\n'
                             'Global id = {}, academic year = {}, attestation_type = {}.'
                             .format(global_id, academic_year, attestation_type))
        except Exception:
            logger.exception('Exception arose when fetching student attestation.'
                             'Global id = {}, academic year = {}, attestation_type = {}.'
                             .format(global_id, academic_year, attestation_type))
    return None


def _fetch_with_basic_auth(server_top_url, document_url):
    password_mgr = urllib.request.HTTPPasswordMgrWithDefaultRealm()
    username = settings.ATTESTATION_CONFIG.get('SERVER_TO_FETCH_USER')
    password = settings.ATTESTATION_CONFIG.get('SERVER_TO_FETCH_PASSWORD')
    password_mgr.add_password(None, server_top_url, username, password)
    handler = urllib.request.HTTPBasicAuthHandler(password_mgr)
    opener = urllib.request.build_opener(handler)

    with opener.open(document_url) as response:
        return response.read()

