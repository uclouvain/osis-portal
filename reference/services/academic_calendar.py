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
import logging
from types import SimpleNamespace

import osis_reference_sdk
import urllib3
from django.conf import settings
from osis_reference_sdk.api import academic_calendars_api
from osis_reference_sdk.model.paginated_academic_calendars import PaginatedAcademicCalendars

from base.models.person import Person
from frontoffice.settings.osis_sdk import reference as reference_sdk, utils

logger = logging.getLogger(settings.DEFAULT_LOGGER)


class AcademicCalendarService:
    @staticmethod
    def get_academic_calendar_list(person: Person, **kwargs) -> PaginatedAcademicCalendars:
        configuration = reference_sdk.build_configuration()
        with osis_reference_sdk.ApiClient(configuration) as api_client:
            api_instance = academic_calendars_api.AcademicCalendarsApi(api_client)
            try:
                enrollments = api_instance.academic_calendars_list(
                    **utils.build_mandatory_auth_headers(person),
                    **kwargs
                )
            except (osis_reference_sdk.ApiException, urllib3.exceptions.HTTPError,) as e:
                # Run in degraded mode in order to prevent crash all app
                logger.error(e)
                enrollments = SimpleNamespace(**{'results': [], 'count': 0})
        return enrollments
