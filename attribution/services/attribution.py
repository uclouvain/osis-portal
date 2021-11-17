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
from typing import List

import osis_attribution_sdk
import urllib3
from django.conf import settings
from osis_attribution_sdk.api import attribution_api

from base.models.person import Person
from frontoffice.settings.osis_sdk import attribution as attribution_sdk, utils

logger = logging.getLogger(settings.DEFAULT_LOGGER)


class AttributionService:
    @staticmethod
    def get_attributions_list(year: int, person: Person, with_effective_class_repartition=False) -> List:
        configuration = attribution_sdk.build_configuration()
        with osis_attribution_sdk.ApiClient(configuration) as api_client:
            api_instance = attribution_api.AttributionApi(api_client)
            try:
                attributions = sorted(
                    api_instance.attributions_list(
                        year=str(year),
                        global_id=person.global_id,
                        with_effective_class_repartition=with_effective_class_repartition,
                        **utils.build_mandatory_auth_headers(person)
                    ),
                    key=lambda attribution: attribution.code
                )
            except (osis_attribution_sdk.ApiException, urllib3.exceptions.HTTPError,) as e:
                # Run in degraded mode in order to prevent crash all app
                logger.error(e)
                attributions = []
        return attributions
