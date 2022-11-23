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

import osis_learning_unit_sdk
from osis_learning_unit_sdk.api import classe_api
from osis_learning_unit_sdk.model.classe import Classe

from base.services.utils import call_api
from frontoffice.settings.osis_sdk import learning_unit as learning_unit_sdk

from base.models.person import Person


class ClasseService:
    @staticmethod
    def rechercher_classes(
            person: 'Person',
            annee: int = None,
            code: str = None,
            codes: List[str] = None,
            intitule: str = None

    ) -> List['Classe']:
        search_parameters = dict(
            annee=annee,
            code=code,
            codes=codes,
            intitule=intitule,
        )
        for key, value in list(search_parameters.items()):
            if value is None:
                del search_parameters[key]

        return _classe_api_call(
            person,
            "get_classes",
            **search_parameters
        )


_classe_api_call = partial(call_api, learning_unit_sdk, osis_learning_unit_sdk, classe_api.ClasseApi)
