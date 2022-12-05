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
from decimal import Decimal
from typing import List, Optional

import attr
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.functional import cached_property
from django.views.generic import TemplateView
from osis_inscription_cours_sdk.model.demande_particuliere import DemandeParticuliere
from osis_inscription_cours_sdk.model.programme_annuel_etudiant import ProgrammeAnnuelEtudiant

from base.services.utils import ServiceException
from base.templatetags.sort_extra import unaccent
from education_group.services.mini_training import MiniTrainingService
from inscription_aux_cours import formatter
from inscription_aux_cours.services.cours import CoursService
from inscription_aux_cours.services.demande_particuliere import DemandeParticuliereService
from inscription_aux_cours.views.common import InscriptionAuxCoursViewMixin
from learning_unit.services.classe import ClasseService
from learning_unit.services.learning_unit import LearningUnitService


@attr.dataclass(auto_attribs=True, frozen=True, slots=True)
class Inscription:
    code: str
    intitule: str
    credits: Decimal


@attr.dataclass(auto_attribs=True, frozen=True, slots=True)
class InscriptionsParContexte:
    intitule: str
    cours: List[Inscription]


@attr.dataclass(auto_attribs=True, frozen=True, slots=True)
class PropositionProgrammeAnnuel:
    inscriptions_par_contexte: List['InscriptionsParContexte']

    @property
    def total_credits(self) -> 'Decimal':
        return sum([
            Decimal(cours.credits)
            for contexte in self.inscriptions_par_contexte
            for cours in contexte.cours
            if cours.credits
        ])

    @property
    def a_des_inscriptions(self) -> bool:
        return any(
            [inscription for contexte in self.inscriptions_par_contexte for inscription in contexte.cours]
        )


class RecapitulatifView(LoginRequiredMixin, InscriptionAuxCoursViewMixin, TemplateView):
    name = "recapitulatif"

    template_name = "inscription_aux_cours/cours/recapitulatif.html"

    @cached_property
    def programme_annuel(self) -> 'ProgrammeAnnuelEtudiant':
        return CoursService().recuperer_programme_annuel(self.person, self.code_programme)

    @property
    def codes_cours_du_programme_annuel(self) -> List[str]:
        codes_cours_tronc_commun = [cours['code'] for cours in self.programme_annuel['tronc_commun']]
        codes_cours_mini_formations = [
            cours['code']
            for mini_formation in self.programme_annuel['mini_formations']
            for cours in mini_formation['cours']
        ]
        return codes_cours_tronc_commun + codes_cours_mini_formations

    @cached_property
    def details_unites_enseignement(self):
        result = LearningUnitService.search_learning_units(
            self.person,
            year=self.annee_academique,
            learning_unit_codes=self.codes_cours_du_programme_annuel
        )
        return {learning_unit['acronym']: learning_unit for learning_unit in result}

    @cached_property
    def details_classes(self):
        result = ClasseService.rechercher_classes(
            self.person,
            annee=self.annee_academique,
            codes=self.codes_cours_du_programme_annuel
        )
        return {classe['code']: classe for classe in result}

    @cached_property
    def details_mini_formation(self):
        codes_mini_formation = [mini_formation['code'] for mini_formation in self.programme_annuel['mini_formations']]
        result = MiniTrainingService().search(self.person, year=self.annee_academique, codes=codes_mini_formation)
        return {mini_formation.code: mini_formation for mini_formation in result}

    @cached_property
    def programme_annuel_avec_details_cours(self) -> 'PropositionProgrammeAnnuel':
        inscriptions_tronc_commun = InscriptionsParContexte(
            intitule=formatter.get_intitule_programme(self.programme),
            cours=self._build_cours(self.programme_annuel['tronc_commun'])
        )
        inscriptions_aux_mini_formations = [
            InscriptionsParContexte(
                intitule=self.details_mini_formation[mini_formation['code']]['title'],
                cours=self._build_cours(mini_formation['cours'])
            ) for mini_formation in self.programme_annuel['mini_formations']
        ]
        inscriptions_aux_mini_formations.sort(key=lambda contexte: unaccent(contexte.intitule))
        inscriptions = [inscriptions_tronc_commun] + inscriptions_aux_mini_formations \
            if inscriptions_tronc_commun.cours else inscriptions_aux_mini_formations
        return PropositionProgrammeAnnuel(
            inscriptions_par_contexte=inscriptions
        )

    def _build_cours(self, cours_par_contexte) -> List['Inscription']:
        result = []
        for cours in cours_par_contexte:
            code = cours['code']
            inscription = Inscription(
                code=code,
                credits=cours['credits'],
                intitule=self.details_unites_enseignement[code]['title']
                if code in self.details_unites_enseignement
                else self.details_classes[code]['intitule']
            )
            result.append(inscription)
        return result

    @cached_property
    def demande_particuliere(self) -> Optional['DemandeParticuliere']:
        try:
            return DemandeParticuliereService().recuperer(self.person, self.code_programme)
        except ServiceException:
            return None

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            'programme_annuel': self.programme_annuel_avec_details_cours,
            'demande_particuliere': self.demande_particuliere
        }
