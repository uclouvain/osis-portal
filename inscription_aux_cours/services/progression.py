#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2023 Université catholique de Louvain (http://www.uclouvain.be)
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
from functools import partial

import osis_parcours_interne_sdk
from osis_parcours_interne_sdk.api import progression_api
from osis_parcours_interne_sdk.model.progression_de_bloc1 import ProgressionDeBloc1
from osis_parcours_interne_sdk.model.progression_de_complement import ProgressionDeComplement
from osis_parcours_interne_sdk.model.progression_de_cycle import ProgressionDeCycle

from base.models.person import Person
from base.services.utils import call_api
from frontoffice.settings.osis_sdk import progression as progression_sdk


class ProgressionService:
    @staticmethod
    def recuperer_progression_de_cycle(person: 'Person', sigle_programme: str) -> 'ProgressionDeCycle':
        return _progression_api_call(person, "get_progression_de_cycle", sigle_programme=sigle_programme)

    @staticmethod
    def recuperer_progression_de_complement(person: 'Person', sigle_programme: str) -> 'ProgressionDeComplement':
        return _progression_api_call(person, "get_progression_de_complement", sigle_programme=sigle_programme)

    @staticmethod
    def recuperer_progression_de_bloc_1(person: 'Person', sigle_programme: str) -> 'ProgressionDeBloc1':
        return _progression_api_call(person, "get_progression_de_bloc_1", sigle_programme=sigle_programme)


_progression_api_call = partial(call_api, progression_sdk, osis_parcours_interne_sdk, progression_api.ProgressionApi)
