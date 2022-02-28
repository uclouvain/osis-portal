##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2021 Université catholique de Louvain (http://www.uclouvain.be)
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
import logging
from typing import List, Optional

import osis_assessments_sdk
import urllib3
from django.conf import settings
from django.http import Http404
from osis_assessments_sdk.api import score_encoding_api, attendance_mark_api
from osis_assessments_sdk.model.attendance_mark_calendar import AttendanceMarkCalendar
from osis_assessments_sdk.model.progress_overview import ProgressOverview

from base.models.person import Person
from frontoffice.settings.osis_sdk import assessments as assessments_sdk
from frontoffice.settings.osis_sdk.utils import build_mandatory_auth_headers

logger = logging.getLogger(settings.DEFAULT_LOGGER)


class AssessmentsService:

    @staticmethod
    def get_current_session(person: Person, **kwargs):
        return _score_encoding_api_call(person, "get_current_session")

    @staticmethod
    def get_next_session(person: Person, **kwargs):
        return _score_encoding_api_call(person, "get_next_session")

    @staticmethod
    def get_previous_session(person: Person, **kwargs):
        return _score_encoding_api_call(person, "get_previous_session")

    @staticmethod
    def get_score_sheet_pdf(learning_unit_code: str, person: Person, **kwargs):
        configuration = assessments_sdk.build_configuration()
        with osis_assessments_sdk.ApiClient(configuration) as api_client:
            api_instance = score_encoding_api.ScoreEncodingApi(api_client)
            try:
                return api_instance.score_sheets_pdf_export(
                    codes=[learning_unit_code],
                    **build_mandatory_auth_headers(person),
                )
            except (osis_assessments_sdk.ApiException, urllib3.exceptions.HTTPError,) as e:
                # Run in degraded mode in order to prevent crash all app
                logger.error(e)
                return {'error_body': e.body, 'error_status': e.status}

    @staticmethod
    def get_xls_score_sheet(learning_unit_code: str, person: Person, **kwargs):
        configuration = assessments_sdk.build_configuration()
        with osis_assessments_sdk.ApiClient(configuration) as api_client:
            api_instance = score_encoding_api.ScoreEncodingApi(api_client)
            try:
                return api_instance.score_sheet_xls_export(
                    code=learning_unit_code,
                    **build_mandatory_auth_headers(person),
                )
            except (osis_assessments_sdk.ApiException, urllib3.exceptions.HTTPError,) as e:
                # Run in degraded mode in order to prevent crash all app
                logger.error(e)
                return {'error_body': e.body, 'error_status': e.status}

    @staticmethod
    def get_score_responsible_list(learning_unit_codes: List[str], year: int, person: Person, **kwargs):
        configuration = assessments_sdk.build_configuration()
        with osis_assessments_sdk.ApiClient(configuration) as api_client:
            api_instance = score_encoding_api.ScoreEncodingApi(api_client)
            try:
                return api_instance.get_score_responsible_list(
                    learning_unit_codes=learning_unit_codes,
                    year=year,
                    **build_mandatory_auth_headers(person),
                )
            except (osis_assessments_sdk.ApiException, urllib3.exceptions.HTTPError,) as e:
                # Run in degraded mode in order to prevent crash all app
                logger.error(e)
                return {'error_body': e.body, 'error_status': e.status}

    @staticmethod
    def get_overview(person: Person, **kwargs) -> ProgressOverview:
        configuration = assessments_sdk.build_configuration()
        with osis_assessments_sdk.ApiClient(configuration) as api_client:
            api_instance = score_encoding_api.ScoreEncodingApi(api_client)
            try:
                progress_overview = api_instance.get_overview(
                    **build_mandatory_auth_headers(person),
                    **kwargs
                )
            except (osis_assessments_sdk.ApiException, urllib3.exceptions.HTTPError,) as e:
                # Run in degraded mode in order to prevent crash all app
                logger.error(e)
                progress_overview = None
        return progress_overview


class AttendanceMarkRemoteCalendar(object):

    def __init__(self, person: Person):
        self._calendars = _assessment_api_call(
            person,
            'attendancemarkscalendars_list'
        ) or []  # type: List[AttendanceMarkCalendar]

    def get_target_years_opened(self) -> List[int]:
        """
        Return list of year authorized based on today
        """
        return [academic_event.authorized_target_year for academic_event in self.get_opened_academic_events()]

    def get_opened_academic_events(self) -> List[AttendanceMarkCalendar]:
        """
        Return all current academic event opened based on today
        """
        return [academic_event for academic_event in self._calendars if academic_event.is_open]

    def get_previous_academic_event(self) -> Optional[AttendanceMarkCalendar]:
        """
        Return previous academic event based on today
        """
        events_filtered = [
            event for event in self._calendars if
            event.end_date is not None and event.end_date < datetime.date.today()
        ]
        return events_filtered[-1] if events_filtered else None

    def get_next_academic_event(self, date=None) -> Optional[AttendanceMarkCalendar]:
        """
        Return next academic event based on today
        """
        events_filtered = [event for event in self._calendars if event.start_date > datetime.date.today()]
        return events_filtered[0] if events_filtered else None


def _score_encoding_api_call(person: Person, method_to_call: str):
    configuration = assessments_sdk.build_configuration()
    with osis_assessments_sdk.ApiClient(configuration) as api_client:
        api_instance = score_encoding_api.ScoreEncodingApi(api_client)
        try:
            class_method = getattr(api_instance, method_to_call)
            result = class_method(**build_mandatory_auth_headers(person),)
        except (osis_assessments_sdk.ApiException, urllib3.exceptions.HTTPError, Http404,) as e:
            logger.error(e)
            return None
    return result


def _assessment_api_call(person: Person, method_to_call: str):
    configuration = assessments_sdk.build_configuration()
    with osis_assessments_sdk.ApiClient(configuration) as api_client:
        api_instance = attendance_mark_api.AttendanceMarkApi(api_client)
        try:
            class_method = getattr(api_instance, method_to_call)
            result = class_method(**build_mandatory_auth_headers(person),)
        except (osis_assessments_sdk.ApiException, urllib3.exceptions.HTTPError, Http404,) as e:
            logger.error(e)
            return None
    return result
