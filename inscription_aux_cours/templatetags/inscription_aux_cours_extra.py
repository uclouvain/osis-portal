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
import urllib.parse
from typing import List, Optional

from django import template
from django.conf import settings
from osis_inscription_cours_sdk.model.inscription_mini_formation import InscriptionMiniFormation
from osis_inscription_cours_sdk.model.mini_formation import MiniFormation
from osis_program_management_sdk.model.programme import Programme

from inscription_aux_cours import formatter
from inscription_aux_cours.data.proposition_programme_annuel import PropositionProgrammeAnnuel
from inscription_aux_cours.views.cours.formulaire import InscriptionAUnCoursHorsProgramme
from program_management.services.programme import ProgrammeService

register = template.Library()



@register.filter
def get_inscription_a_la_mini_formation(
        mini_formation: 'MiniFormation',
        inscriptions_mini_formations: List['InscriptionMiniFormation']
) -> Optional['InscriptionMiniFormation']:
    return next(
        (inscription for inscription in inscriptions_mini_formations if inscription.code_mini_formation == mini_formation.code),
        None
    )


@register.filter
def filtrer_inscriptions_hors_programme_par_contexte(
        inscriptions: List['InscriptionAUnCoursHorsProgramme'],
        code_mini_formation: str = None
) -> List['InscriptionAUnCoursHorsProgramme']:
    if not code_mini_formation:
        return [inscription for inscription in inscriptions if not inscription.code_mini_formation]
    return [inscription for inscription in inscriptions if inscription.code_mini_formation == code_mini_formation]


@register.simple_tag
def get_lien_condition_access(programme: 'Programme', mini_formation: 'MiniFormation') -> str:
    if ProgrammeService.est_bachelier(programme):
        return f"{settings.INSTITUTION_URL}prog-{programme.annee}-{_clean_sigle_mini_formation(mini_formation.sigle)}-cond_adm"
    sigle_formation = ProgrammeService.get_sigle_formation(programme)
    return f"{settings.INSTITUTION_URL}prog-{programme.annee}-{sigle_formation}-programme"


def _clean_sigle_mini_formation(sigle: str) -> str:
    return sigle.split('[')[0]

@register.simple_tag
def get_lien_horaire_cours(programme_annuel: 'PropositionProgrammeAnnuel') -> str:

    codes_cours = [
        _format_code_cours_pour_lien_horaire(cours.code)
        for contexte in programme_annuel.inscriptions_par_contexte
        for cours in contexte.cours
    ]
    return settings.COURSES_SCHEDULE_URL.format(
        codes_cours=urllib.parse.quote(",".join(codes_cours))
    )


def _format_code_cours_pour_lien_horaire(code: str) -> str:
    separation_classe_magistrale = '-'
    separation_classe_pratique = '_'
    return code.replace(separation_classe_pratique, "").replace(separation_classe_magistrale, "")


@register.filter
def get_sigle_programme(programme: 'Programme') -> str:
    if programme.version:
        return f"{programme.sigle}[{programme.version}]"
    return f"{programme.sigle}"


@register.filter
def get_intitule_programme(programme: 'Programme') -> str:
    return formatter.get_intitule_programme(programme)
