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

import osis_inscription_cours_sdk
import urllib3
from django.conf import settings
from django.http import Http404
from osis_inscription_cours_sdk.model.liste_mini_formations import ListeMiniFormations
from osis_inscription_cours_sdk.api import mini_formation_api

from base.models.person import Person
from frontoffice.settings.osis_sdk import inscription_aux_cours as inscription_aux_cours_sdk
from frontoffice.settings.osis_sdk.utils import build_mandatory_auth_headers

logger = logging.getLogger(settings.DEFAULT_LOGGER)


class MiniFormationService:

    @staticmethod
    def get_mini_formations_inscriptibles(sigle_formation: str, person: Person) -> 'ListeMiniFormations':
        return _mini_formation_api_call(person, "mini_formations_inscriptibles", sigle_formation=sigle_formation)


def _mini_formation_api_call(person: Person, method_to_call: str, **kwargs):
    configuration = inscription_aux_cours_sdk.build_configuration()
    with osis_inscription_cours_sdk.ApiClient(configuration) as api_client:
        api_instance = mini_formation_api.MiniFormationApi(api_client)
        try:
            class_method = getattr(api_instance, method_to_call)
            result = class_method(**build_mandatory_auth_headers(person), **kwargs)
        except (osis_inscription_cours_sdk.ApiException, urllib3.exceptions.HTTPError, Http404,) as e:
            logger.error(e)
            return None
    return result


