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
from functools import partial
from typing import List

import osis_inscription_cours_sdk
from django.conf import settings
from osis_inscription_cours_sdk.api import mini_formation_api
from osis_inscription_cours_sdk.model.inscription_mini_formation import InscriptionMiniFormation
from osis_inscription_cours_sdk.model.inscrire_a_une_mini_formation import InscrireAUneMiniFormation
from osis_inscription_cours_sdk.model.liste_mini_formations import ListeMiniFormations

from base.models.person import Person
from base.services.utils import call_api
from frontoffice.settings.osis_sdk import inscription_aux_cours as inscription_aux_cours_sdk

logger = logging.getLogger(settings.DEFAULT_LOGGER)


class MiniFormationService:

    @staticmethod
    def get_mini_formations_inscriptibles(person: Person, sigle_formation: str) -> 'ListeMiniFormations':
        return _mini_formation_api_call(
            person,
            "mini_formations_inscriptibles",
            sigle_formation=sigle_formation
        )

    @staticmethod
    def inscrire_a_une_mini_formation(person: Person, sigle_formation: str, code_mini_formation: str):
        cmd = InscrireAUneMiniFormation(
            code_mini_formation=code_mini_formation
        )
        return _mini_formation_api_call(
            person,
            'enroll_mini_formation',
            sigle_formation=sigle_formation,
            inscrire_a_une_mini_formation=cmd
        )

    @staticmethod
    def desinscrire_a_une_mini_formation(person: Person, sigle_formation: str, code_mini_formation: str):
        return _mini_formation_api_call(
            person,
            'unenroll_mini_formation',
            sigle_formation=sigle_formation,
            code_mini_formation=code_mini_formation
        )

    @staticmethod
    def get_inscriptions(person: Person, sigle_formation: str) -> List['InscriptionMiniFormation']:
        return _mini_formation_api_call(
            person,
            'inscriptions_mini_formations',
            sigle_formation=sigle_formation
        )


_mini_formation_api_call = partial(
    call_api,
    inscription_aux_cours_sdk,
    osis_inscription_cours_sdk,
    mini_formation_api.MiniFormationApi
)
