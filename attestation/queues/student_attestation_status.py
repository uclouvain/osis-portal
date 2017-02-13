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
import datetime
from django.conf import settings
from frontoffice.queue.queue_listener import AttestationStatusClient
from attestation.models import attestation_status as mdl_attestation_status


def get_or_fetch(student):
    attestation_statuses = mdl_attestation_status.find_by_student(student)
    if not attestation_statuses or _has_to_be_updated(attestation_statuses.first()):
        json_attestation_statuses = _fetch_json_attestation_statuses(student.registration_id)
        if json_attestation_statuses:
            attestation_statuses = _save_data_from_json(student, json_attestation_statuses)
    return attestation_statuses


def _fetch_json_attestation_statuses(registration_id):
    message = _generate_registration_id_message(registration_id)
    client = AttestationStatusClient()
    json_data = client.call(message)
    json_attestation_statuses = None
    if json_data:
        json_attestation_statuses = json.loads(json_data.decode("utf-8"))
    return json_attestation_statuses


def _generate_registration_id_message(registration_id):
    if registration_id:
        return json.dumps({'registration_id': registration_id})
    return None


def _save_data_from_json(student, json_attestation_statuses):
    attestation_statuses_from_json = json_attestation_statuses.get("attestation_statuses")
    attestation_statuses = list()
    for attestation_status_dict in attestation_statuses_from_json:
        attestation_status = _make_attestation_status(student, attestation_status_dict)
        if attestation_status:
            attestation_status.save()
            attestation_statuses.append(attestation_status)
    return attestation_statuses


def _make_attestation_status(student, attestation_status_dict):
    attestation_dict_type = attestation_status_dict.get('attestation_type')
    printed = attestation_status_dict.get('printed')
    available = attestation_status_dict.get('available')
    attestation_status = mdl_attestation_status.AttestationStatus(student=student,
                                                                  attestation_type=attestation_dict_type,
                                                                  printed=printed,
                                                                  available=available,
                                                                  update_date=_default_update_date())
    return attestation_status


def _default_update_date():
    now = datetime.datetime.now()
    update_delta_hours = settings.PERFORMANCE_CONFIG.get('UPDATE_DELTA_HOURS_AFTER_CONSUMPTION')
    timedelta = datetime.timedelta(hours=update_delta_hours)
    return now + timedelta


def _has_to_be_updated(attestation_status):
    now = datetime.datetime.now()
    return attestation_status.update_date and attestation_status.update_date <= now
