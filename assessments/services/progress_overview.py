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

import osis_assessments_sdk
import urllib3
from django.conf import settings
from osis_assessments_sdk.api import score_encoding_api
from osis_assessments_sdk.model.progress_overview import ProgressOverview

from base.models.person import Person
from frontoffice.settings.osis_sdk import assessments as assessments_sdk, utils

logger = logging.getLogger(settings.DEFAULT_LOGGER)


class ProgressOverviewService:

    @staticmethod
    def get_progress_overview(person: Person, **kwargs) -> ProgressOverview:
        configuration = assessments_sdk.build_configuration()
        with osis_assessments_sdk.ApiClient(configuration) as api_client:
            api_instance = score_encoding_api.ScoreEncodingApi(api_client)
            try:
                progress_overview = api_instance.get_progress_overview(
                    **utils.build_mandatory_auth_headers(person),
                    **kwargs
                )
            except (osis_assessments_sdk.ApiException, urllib3.exceptions.HTTPError,) as e:
                # Run in degraded mode in order to prevent crash all app
                logger.error(e)
                progress_overview = None
        return progress_overview
