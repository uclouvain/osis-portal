#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2022 Université catholique de Louvain (http://www.uclouvain.be)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
import logging

import osis_education_group_sdk
import urllib3
from django.conf import settings
from osis_education_group_sdk.api import trainings_api

from base.models.person import Person
from frontoffice.settings.osis_sdk import education_group as education_group_sdk, utils

logger = logging.getLogger(settings.DEFAULT_LOGGER)


class EducationGroupService:
    @staticmethod
    def get_program_title(acronym: str, year: int, person: Person, **kwargs) -> str:
        configuration = education_group_sdk.build_configuration()
        with osis_education_group_sdk.ApiClient(configuration) as api_client:
            api_instance = trainings_api.TrainingsApi(api_client)
            try:
                return api_instance.trainingstitle_read(
                    acronym=acronym,
                    year=year,
                    **utils.build_mandatory_auth_headers(person),
                ).title
            except (osis_education_group_sdk.ApiException, urllib3.exceptions.HTTPError,) as e:
                # Run in degraded mode in order to prevent crash all app
                logger.error(e)
        return ""
