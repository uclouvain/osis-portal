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
from functools import partial
from typing import List

import osis_program_management_sdk
from osis_program_management_sdk.api import programme_api
from osis_program_management_sdk.model.programme import Programme

from base.models.person import Person
from base.services.utils import call_api
from frontoffice.settings.osis_sdk import program_management as program_management_sdk

TYPE_BACHELIER = 'BACHELOR'
TYPE_DOCTORAT = 'PHD'
TYPE_FORMATION_DOCTORALE = 'FORMATION_PHD'


class ProgrammeService:
    @staticmethod
    def rechercher(person: 'Person', annee: int, codes: List[str]) -> List['Programme']:
        return _programme_api_call(person, "programmes_list", annee=annee, codes=codes)

    @staticmethod
    def est_bachelier(programme: 'Programme') -> bool:
        return programme.type == TYPE_BACHELIER

    @staticmethod
    def est_formation_doctorale(programme: 'Programme') -> bool:
        return programme.type == TYPE_FORMATION_DOCTORALE

    @staticmethod
    def est_doctorat(programme: 'Programme') -> bool:
        return programme.type == TYPE_DOCTORAT

    @staticmethod
    def get_sigle_formation(programme: 'Programme') -> str:
        sigle_programme = programme.sigle
        sigle_formation = sigle_programme
        if '2MS/' in sigle_programme:
            sigle_formation = sigle_programme[0:sigle_programme.index('2MS/') + 2]
        elif "2MA" in sigle_programme:
            sigle_formation = sigle_programme[0:sigle_programme.index('2MA') + 2]
        return sigle_formation


_programme_api_call = partial(
    call_api,
    program_management_sdk,
    osis_program_management_sdk,
    programme_api.ProgrammeApi
)
