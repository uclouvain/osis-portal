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
import urllib.parse
from decimal import Decimal
from typing import List, Optional

from django import template
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from osis_inscription_cours_sdk.model.inscription_aun_cours import InscriptionAUnCours
from osis_inscription_cours_sdk.model.inscription_mini_formation import InscriptionMiniFormation
from osis_inscription_cours_sdk.model.mini_formation import MiniFormation
from osis_inscription_cours_sdk.model.programme_annuel_etudiant import ProgrammeAnnuelEtudiant
from osis_program_management_sdk.model.programme import Programme

from inscription_aux_cours import formatter
from inscription_aux_cours.data.proposition_programme_annuel import PropositionProgrammeAnnuel
from inscription_aux_cours.services.code_unite_enseignement import CodeParser
from inscription_aux_cours.views.cours.formulaire import InscriptionAUnCoursHorsProgramme
from program_management.services.programme import ProgrammeService

register = template.Library()


@register.filter
def formater_volumes(obj) -> str:
    return _formater_volumes(obj['volume_annuel_pm'], obj['volume_annuel_pp'])


def _formater_volumes(volume_pm: Decimal, volume_pp: Decimal) -> str:
    vol_tot_pm = f"{Decimal(volume_pm) or Decimal(0.0):g}h" if volume_pm else ''
    vol_tot_pp = ''
    if volume_pp:
        vol_tot_pp = "{operateur}{total_pp:g}h".format(
            operateur=" + " if volume_pm and volume_pp else "",
            total_pp=Decimal(volume_pp),
        )
    return f"[{vol_tot_pm}{vol_tot_pp}]" if vol_tot_pm or vol_tot_pp else '-'


@register.filter
def est_inscrit_a_la_mini_formation(
    mini_formation: 'MiniFormation', inscriptions_mini_formations: List['InscriptionMiniFormation']
):
    codes_mini_formations_inscrites = {inscription.code_mini_formation for inscription in inscriptions_mini_formations}
    return mini_formation.code in codes_mini_formations_inscrites


@register.filter
def get_inscription_a_la_mini_formation(
    mini_formation: 'MiniFormation', inscriptions_mini_formations: List['InscriptionMiniFormation']
) -> Optional['InscriptionMiniFormation']:
    return next(
        (
            inscription
            for inscription in inscriptions_mini_formations
            if inscription.code_mini_formation == mini_formation.code
        ),
        None,
    )


@register.filter
def est_inscrit_au_cours(cours: 'InscriptionAUnCours', programme_annuel_etudiant: ProgrammeAnnuelEtudiant):
    codes_cours = {inscription.code for inscription in programme_annuel_etudiant.tronc_commun}
    codes_cours |= {
        inscription.code
        for mini_formation in programme_annuel_etudiant.mini_formations
        for inscription in mini_formation.cours
    }
    return cours['code'] in codes_cours


@register.filter
def filtrer_inscriptions_hors_programme_par_contexte(
    inscriptions: List['InscriptionAUnCoursHorsProgramme'], code_mini_formation: str = None
) -> List['InscriptionAUnCoursHorsProgramme']:
    if not code_mini_formation:
        return [inscription for inscription in inscriptions if not inscription.code_mini_formation]
    return [inscription for inscription in inscriptions if inscription.code_mini_formation == code_mini_formation]


@register.simple_tag
def get_message_condition_access(annee: int, mini_formation: 'MiniFormation') -> str:
    lien = f"{settings.INSTITUTION_URL}prog-{annee}-{mini_formation.sigle}-cond_adm"
    return _(
        "This minor has admission requirements, please consult the registration procedure: {lien_condition_acces}"
    ).format(lien_condition_acces=f"<a href='{lien}'>{lien}</a>")


@register.simple_tag
def get_lien_condition_access(programme: 'Programme', mini_formation: 'MiniFormation') -> str:
    if ProgrammeService.est_bachelier(programme):
        return (
            f"{settings.INSTITUTION_URL}prog-{programme.annee}-"
            f"{_clean_sigle_mini_formation(mini_formation.sigle)}-cond_adm"
        )
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
    return settings.COURSES_SCHEDULE_URL.format(codes_cours=urllib.parse.quote(",".join(codes_cours)))


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


@register.filter
def get_code_ue_sans_classe(code: str) -> str:
    return CodeParser.get_code_unite_enseignement(code)
