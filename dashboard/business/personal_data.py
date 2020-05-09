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
import traceback
from urllib import error, request
from base.models import student as student_mdl, person as person_mdl
from django.conf import settings

logger = logging.getLogger(settings.DEFAULT_LOGGER)


def __fetch_student_personal_data(person):
    data = {
        'registration_service_url': settings.REGISTRATION_ADMINISTRATION_URL
    }
    try:
        server_top_url = settings.ESB_URL
        personal_data_path = settings.STUDENT_PERSONAL_DATA_PATH
        main_data_path = settings.STUDENT_MAIN_DATA_PATH
        personal_data_url = server_top_url + personal_data_path.format(person.global_id)
        main_data_url = server_top_url + main_data_path.format(person.global_id)
        personal_data = get_data_from_esb(personal_data_url)
        main_data = get_data_from_esb(main_data_url)
        data.update(personal_data.get('return'))
        data['main_data'] = main_data.get('lireDossierEtudiantResponse').get('return')
    except error.HTTPError:
        log_trace = traceback.format_exc()
        logger.warning('Error when querying WebService: \n {}'.format(log_trace))
    except Exception:
        log_trace = traceback.format_exc()
        logger.warning('Error when returning student personal data: \n {}'.format(log_trace))
    finally:
        return data


def get_student_personal_data(user):
    student = student_mdl.find_by_user(user)
    data = None
    if student:
        person = person_mdl.find_by_user(user)
        data = __fetch_student_personal_data(person)
    return data


def get_data_from_esb(url):
    logger.info('URL ESB : '+url)
    esb_headers = {"Authorization": settings.ESB_AUTHORIZATION, "Content-Type": settings.ESB_CONTENT_TYPE}
    esb_request = request.Request(url, headers=esb_headers)
    esb_connection = request.urlopen(esb_request, timeout=settings.ESB_TIMEOUT)
    esb_response = esb_connection.read().decode(settings.ESB_ENCODING)
    esb_connection.close()
    esb_data = json.loads(esb_response)
    return esb_data
