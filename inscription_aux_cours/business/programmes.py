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
from copy import copy
from typing import List

from osis_offer_enrollment_sdk.model.inscription import Inscription
from osis_program_management_sdk.model.programme import Programme

from base.models.person import Person
from base.services.offer_enrollment import InscriptionFormationsService
from base.utils.string_utils import decapitalize
from program_management.services.programme import ProgrammeService
from django.utils.translation import gettext_lazy as _


def recuperer_programme(
        person: 'Person',
        annee: int,
        code_programme: str
) -> 'Programme':
    inscriptions = InscriptionFormationsService.mes_inscriptions(person, annee).inscriptions
    inscriptions_au_programme = [
        inscription
        for inscription in inscriptions
        if inscription.code_programme == code_programme
    ]
    return recuperer_programmes_inscrits(person, annee, inscriptions_au_programme)[0]


def recuperer_programmes_inscrits(
        person: 'Person',
        annee: int,
        inscriptions: List['Inscription']
) -> List['Programme']:
    if not inscriptions:
        return []

    codes = [inscription.code_programme for inscription in inscriptions]
    programmes = ProgrammeService.rechercher(person, annee=annee, codes=codes)
    return [
        _modifier_programme_pour_premiere_annee(programme)
        if _est_inscrit_en_tant_que_premiere_annee(programme, inscriptions) else programme
        for programme in programmes
    ]


def _est_inscrit_en_tant_que_premiere_annee(
        programme: 'Programme',
        inscriptions: List['Inscription']
) -> bool:
    inscriptions_premiere_annee = [inscription for inscription in inscriptions if inscription.est_en_premiere_annee]
    code_programmes_premiere_annee = [inscription.code_programme for inscription in inscriptions_premiere_annee]
    return programme.code in code_programmes_premiere_annee


def _modifier_programme_pour_premiere_annee(programme: 'Programme') -> 'Programme':
    programme_transforme = copy(programme)

    programme_transforme.sigle = __transformer_sigle_poure_premiere_annee(programme.sigle)
    programme_transforme.intitule_formation = __transformer_intitule_formation_pour_premiere_annee(
        programme.intitule_formation
    )

    return programme_transforme


def __transformer_sigle_poure_premiere_annee(sigle: str) -> str:
    return sigle.replace('1BA', '11BA')


def __transformer_intitule_formation_pour_premiere_annee(intitule_formation: str) -> str:
    suffix = _('First year of')
    return f"{suffix} {decapitalize(intitule_formation)}"
