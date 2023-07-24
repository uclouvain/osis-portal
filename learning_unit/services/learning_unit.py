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
from typing import List, Dict, Optional

import osis_learning_unit_sdk
import urllib3
from django.conf import settings
from django.http import Http404
from osis_learning_unit_sdk.api import learning_units_api
from osis_learning_unit_sdk.model.effective_class import EffectiveClass
from osis_learning_unit_sdk.model.learning_unit import LearningUnit
from osis_learning_unit_sdk.model.learning_unit_type_enum import LearningUnitTypeEnum

from base.models.person import Person
from frontoffice.settings.osis_sdk import learning_unit as learning_unit_sdk, utils
from frontoffice.settings.osis_sdk.utils import convert_api_enum
from osis_common.utils.debug import profile_db

logger = logging.getLogger(settings.DEFAULT_LOGGER)

LearningUnitTypeEnum = convert_api_enum(LearningUnitTypeEnum)


class LearningUnitService:

    @staticmethod
    def get_learning_units(learning_unit_codes: List[str], year: int, person: Person, **kwargs):
        configuration = learning_unit_sdk.build_configuration()
        with osis_learning_unit_sdk.ApiClient(configuration) as api_client:
            api_instance = learning_units_api.LearningUnitsApi(api_client)
            try:
                learning_units = api_instance.learningunits_list(
                    learning_unit_codes=','.join({str(elem) for elem in learning_unit_codes}),
                    year=year,
                    **utils.build_mandatory_auth_headers(person),
                )
                return learning_units.get('results', {})
            except (osis_learning_unit_sdk.ApiException, urllib3.exceptions.HTTPError,) as e:
                # Run in degraded mode in order to prevent crash all app
                logger.error(e)
                attrs = {'results': [], 'error': e}
                learning_units = SimpleNamespace(**attrs, attribute_map=attrs)
        return learning_units

    @staticmethod
    def get_learning_unit_title(year: int, acronym: str, person: Person) -> str:
        configuration = learning_unit_sdk.build_configuration()
        with osis_learning_unit_sdk.ApiClient(configuration) as api_client:
            api_instance = learning_units_api.LearningUnitsApi(api_client)
            try:
                learning_unit_title = api_instance.learningunitstitle_read(
                    year=year,
                    acronym=acronym,
                    **utils.build_mandatory_auth_headers(person),
                )['title']
            except (osis_learning_unit_sdk.ApiException, urllib3.exceptions.HTTPError,) as e:
                # Run in degraded mode in order to prevent crash all app
                logger.error(e)
                learning_unit_title = ''
        return learning_unit_title

    @staticmethod
    def search_learning_unit_titles(
            year: int,
            person: Person,
            code: Optional[str] = None,
            codes: Optional[List[str]] = None
    ) -> List[Dict]:
        configuration = learning_unit_sdk.build_configuration()
        with osis_learning_unit_sdk.ApiClient(configuration) as api_client:
            api_instance = learning_units_api.LearningUnitsApi(api_client)
            try:
                query_params = {}
                if code:
                    query_params['code'] = code
                if codes:
                    query_params['codes'] = codes

                return api_instance.learning_units_titles_read(
                    year=year,
                    **query_params,
                    **utils.build_mandatory_auth_headers(person),
                )
            except (osis_learning_unit_sdk.ApiException, urllib3.exceptions.HTTPError,) as e:
                # Run in degraded mode in order to prevent crash all app
                logger.error(e)
        return []

    @staticmethod
    def get_effective_classes(year: int, acronym: str, person: Person) -> List[EffectiveClass]:
        configuration = learning_unit_sdk.build_configuration()
        with osis_learning_unit_sdk.ApiClient(configuration) as api_client:
            api_instance = learning_units_api.LearningUnitsApi(api_client)
            try:
                effective_classes = api_instance.get_learning_unit_classes(
                    year=year,
                    acronym=acronym,
                    **utils.build_mandatory_auth_headers(person),
                )
            except (osis_learning_unit_sdk.ApiException, urllib3.exceptions.HTTPError,) as e:
                # Run in degraded mode in order to prevent crash all app
                logger.error(e)
                effective_classes = []
        return effective_classes


def _api_call(person: Person, method_to_call: str, **kwargs):
    configuration = learning_unit_sdk.build_configuration()
    with osis_learning_unit_sdk.ApiClient(configuration) as api_client:
        api_instance = learning_units_api.LearningUnitsApi(api_client)
        try:
            class_method = getattr(api_instance, method_to_call)
            result = class_method(**utils.build_mandatory_auth_headers(person), **kwargs)
        except (osis_learning_unit_sdk.ApiException, urllib3.exceptions.HTTPError, Http404,) as e:
            logger.error(e)
            return None
    return result
