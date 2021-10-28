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
from typing import List

import osis_learning_unit_sdk
import urllib3
from django.conf import settings
from osis_learning_unit_sdk.api import learning_units_api

from base.models.person import Person
from frontoffice.settings.osis_sdk import learning_unit as learning_unit_sdk, utils

logger = logging.getLogger(settings.DEFAULT_LOGGER)


class LearningUnitService:

    @staticmethod
    def get_learning_units(learning_unit_codes: List[str], year: int, person: Person, **kwargs):
        configuration = learning_unit_sdk.build_configuration()
        with osis_learning_unit_sdk.ApiClient(configuration) as api_client:
            api_instance = learning_units_api.LearningUnitsApi(api_client)
            try:
                learning_units = api_instance.learningunits_list(
                    learning_unit_codes=','.join([str(elem) for elem in learning_unit_codes]),
                    year=year,
                    ** utils.build_mandatory_auth_headers(person),
                )
                return learning_units.get('results', {})
            except (osis_learning_unit_sdk.ApiException, urllib3.exceptions.HTTPError,) as e:
                # Run in degraded mode in order to prevent crash all app
                logger.error(e)
                attrs = {'result': None, 'error': e}
                learning_units = SimpleNamespace(**attrs, attribute_map=attrs)
        return learning_units
