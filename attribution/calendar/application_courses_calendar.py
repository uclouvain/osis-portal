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
from typing import List

import urllib3
from django.conf import settings

from frontoffice.settings.osis_sdk import attribution as attribution_sdk
import osis_attribution_sdk

LOGGER = logging.getLogger(settings.DEFAULT_LOGGER)


class ApplicationCoursesRemoteCalendar(object):
    _calendars = []  # type: List[osis_attribution_sdk.models.ApplicationCourseCalendar]

    def __init__(self):
        configuration = attribution_sdk.build_configuration()

        with osis_attribution_sdk.ApiClient(configuration) as api_client:
            api_instance = osis_attribution_sdk.ApplicationApi(api_client)
            try:
                self._calendars = sorted(api_instance.applicationcoursescalendars_list(),
                                         key=lambda academic_event: academic_event.start_date)
            except (osis_attribution_sdk.ApiException, urllib3.exceptions.HTTPError,) as e:
                # Run in degraded mode in order to prevent crash all app
                LOGGER.error(e)
                self._calendars = []

    def get_target_years_opened(self) -> List[int]:
        """
        Return list of year authorized based on today
        """
        return [academic_event.authorized_target_year for academic_event in self.get_opened_academic_events()]

    def get_opened_academic_events(self) -> List[osis_attribution_sdk.models.ApplicationCourseCalendar]:
        """
        Return all current academic event opened based on today
        """
        return [academic_event for academic_event in self._calendars if academic_event.is_open]

    def get_previous_academic_event(self) -> osis_attribution_sdk.models.ApplicationCourseCalendar:
        """
        Return previous academic event based on today
        """
        events_filtered = [
            event for event in self._calendars if
            event.end_date is not None and event.end_date < datetime.date.today()
        ]
        return events_filtered[-1] if events_filtered else None

    def get_next_academic_event(self, date=None) -> osis_attribution_sdk.models.ApplicationCourseCalendar:
        """
        Return next academic event based on today
        """
        events_filtered = [event for event in self._calendars if event.start_date > datetime.date.today()]
        return events_filtered[0] if events_filtered else None
