##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2023 Université catholique de Louvain (http://www.uclouvain.be)
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
import logging
import traceback
from typing import Dict, Optional
from urllib import error

import requests
from django.conf import settings

from base.models import student as student_mdl
from base.models.student import Student

logger = logging.getLogger(settings.DEFAULT_LOGGER)


def _fetch_student_id_data(student: Student) -> Dict:
    data = {'registration_service_url': settings.REGISTRATION_ADMINISTRATION_URL}
    try:
        data['personal_data'] = _get_personal_data(student)
        data['main_data'] = _get_main_data(student)
        data['birth_data'] = _get_birth_data(student)
        data['niss'] = _get_formated_niss(student)
    except error.HTTPError:
        log_trace = traceback.format_exc()
        logger.warning(f'Error when querying WebService: \n {log_trace}')
    except Exception:
        log_trace = traceback.format_exc()
        logger.warning(f'Error when returning student personal data: \n {log_trace}')
    return data


def _get_main_data(student: Student) -> Dict:
    server_top_url = settings.ESB_URL
    main_data_path = settings.STUDENT_ID_DATA.get('MAIN_DATA_PATH')
    main_data_url = server_top_url + main_data_path.format(student.person.global_id)
    main_data = _get_data_from_esb(main_data_url).get('lireDossierEtudiantResponse').get('return')
    main_data['email'] = student.email
    return main_data


def _get_personal_data(student: Student) -> Dict:
    server_top_url = settings.ESB_URL
    personal_data_path = settings.STUDENT_ID_DATA.get('PERSONAL_DATA_PATH')
    personal_data_url = server_top_url + personal_data_path.format(student.person.global_id)
    return _get_data_from_esb(personal_data_url).get('return')


def _get_niss(student: Student) -> int:
    server_top_url = settings.ESB_URL
    niss_data_path = settings.STUDENT_ID_DATA.get('NISS_DATA_PATH')
    niss_data_url = server_top_url + niss_data_path.format(student.person.global_id)
    return _get_data_from_esb(niss_data_url).get('return', {}).get('niss')


def _get_formated_niss(student: Student) -> str:
    niss = str(_get_niss(student))
    return f"{niss[:2]}.{niss[2:4]}.{niss[4:6]}-{niss[6:9]}.{niss[9:]}"


def _get_birth_data(student: Student) -> Dict:
    server_top_url = settings.ESB_URL
    birth_data_path = settings.STUDENT_ID_DATA.get('BIRTH_DATA_PATH')
    birth_data_url = server_top_url + birth_data_path.format(student.person.global_id)
    return _get_data_from_esb(birth_data_url).get('return')


def get_student_id_data(registration_id: str = None) -> Optional[Dict]:
    data, student = None, None
    if registration_id:
        student = student_mdl.find_by_registration_id(registration_id)
    if student:
        data = _fetch_student_id_data(student)
    return data


def _get_data_from_esb(url: str) -> Dict:
    logger.info(f'URL ESB : {url}')
    esb_headers = {"Authorization": settings.ESB_AUTHORIZATION, "Accept": settings.ESB_CONTENT_TYPE}
    response = requests.get(url, headers=esb_headers, timeout=settings.ESB_TIMEOUT)
    return response.json()
