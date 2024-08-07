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
from decimal import Decimal
from typing import List, Optional, Dict

import attr
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.utils.decorators import method_decorator
from django.utils.functional import cached_property
from django.views.decorators.cache import never_cache
from django.views.generic import TemplateView
from osis_inscription_cours_sdk.model.demande_particuliere import DemandeParticuliere
from osis_inscription_cours_sdk.model.programme_annuel_etudiant import ProgrammeAnnuelEtudiant
from osis_learning_unit_sdk.model.classe import Classe

from base.services.utils import ServiceException
from base.utils.string_utils import unaccent
from education_group.services.training import TrainingService
from inscription_aux_cours.forms.cours.demande_particuliere import DemandeParticuliereForm
from inscription_aux_cours.forms.cours.inscription_hors_programme import InscriptionHorsProgrammeForm
from inscription_aux_cours.services.complement import ComplementService
from inscription_aux_cours.services.cours import CoursService
from inscription_aux_cours.services.demande_particuliere import DemandeParticuliereService
from inscription_aux_cours.services.formulaire_inscription import FormulaireInscriptionService
from inscription_aux_cours.services.mini_formation import MiniFormationService
from inscription_aux_cours.services.progression import ProgressionService
from inscription_aux_cours.views.common import CompositionPAEViewMixin
from learning_unit.services.learning_unit import LearningUnitService


@attr.dataclass(frozen=True, slots=True, auto_attribs=True)
class InscriptionAUnCoursHorsProgramme:
    code_mini_formation: str
    code_cours: str
    intitule_cours: str
    credits: Decimal


@method_decorator(never_cache, name='dispatch')
class FormulaireCompositionPAEView(LoginRequiredMixin, CompositionPAEViewMixin, TemplateView):
    name = 'formulaire-inscription-cours'

    # TemplateView
    template_name = "inscription_aux_cours/cours/formulaire.html"

    @cached_property
    def formulaire_inscriptions_cours(self):
        formulaire = FormulaireInscriptionService().recuperer(self.person, self.code_programme)
        FormulaireInscriptionService().marquer_comme_lu(self.person, self.code_programme)
        return formulaire

    @cached_property
    def formulaire_inscription_hors_programme(self) -> 'InscriptionHorsProgrammeForm':
        choix_mini_formations = [
            (formulaire_mini_formation.code_programme, formulaire_mini_formation.intitule_formation)
            for formulaire_mini_formation in self.formulaire_inscriptions_cours.formulaires_mini_formation
            if formulaire_mini_formation.etudiant_autorise_a_ajouter_cours
        ]
        choix_mini_formations.sort(key=lambda choix: unaccent(choix[1]))
        if self.formulaire_inscriptions_cours.formulaire_tronc_commun.etudiant_autorise_a_ajouter_cours:
            choix_mini_formations = [('', self.programme.intitule_formation)] + choix_mini_formations
        return InscriptionHorsProgrammeForm(
            choix_mini_formations,
            initial={'annee': self.annee_academique},
        )

    @cached_property
    def programme_annuel_etudiant(self) -> 'ProgrammeAnnuelEtudiant':
        return CoursService().recuperer_programme_annuel(self.person, self.code_programme)

    @cached_property
    def inscriptions_hors_programme(self) -> List['InscriptionAUnCoursHorsProgramme']:
        result = []  # type: List[InscriptionAUnCoursHorsProgramme]
        result += [
            InscriptionAUnCoursHorsProgramme(
                code_mini_formation="", code_cours=inscription.code, intitule_cours="", credits=inscription.credits
            )
            for inscription in self.formulaire_inscriptions_cours["formulaire_tronc_commun"][
                'inscriptions_hors_programme'
            ]
        ]
        for inscriptions_pour_mini_formation in self.formulaire_inscriptions_cours["formulaires_mini_formation"]:
            result += [
                InscriptionAUnCoursHorsProgramme(
                    code_mini_formation=inscriptions_pour_mini_formation.code_programme,
                    code_cours=inscription.code,
                    intitule_cours="",
                    credits=inscription.credits,
                )
                for inscription in inscriptions_pour_mini_formation['inscriptions_hors_programme']
            ]
        return self._remplir_intitule_cours(result)

    def _remplir_intitule_cours(
        self, inscriptions_hors_programme: List['InscriptionAUnCoursHorsProgramme']
    ) -> List['InscriptionAUnCoursHorsProgramme']:
        if not inscriptions_hors_programme:
            return []
        codes_cours = [cours.code_cours for cours in inscriptions_hors_programme]
        unites_enseignements_par_code = self.recuperer_intitules_unites_enseignement(codes_cours)

        return [
            attr.evolve(
                inscription,
                intitule_cours=unites_enseignements_par_code[inscription.code_cours],
            )
            for inscription in inscriptions_hors_programme
        ]

    def _rechercher_unites_enseignements(self, codes_cours: List[str]) -> Dict[str, 'str']:
        return {
            code: LearningUnitService.get_learning_unit_title(
                year=self.annee_academique, acronym=code, person=self.person
            )
            for code in codes_cours
        }

    @cached_property
    def a_des_mini_formations_inscriptibles(self) -> bool:
        return bool(MiniFormationService().get_inscriptibles(self.person, self.code_programme).mini_formations)

    @cached_property
    def credits_acquis_dans_mini_formations(self) -> Dict[str, str]:
        try:
            credits_acquis = ProgressionService.recuperer_credits_acquis_dans_mini_formations(
                person=self.person, sigle_programme=self.sigle_formation.replace('11BA', '1BA')
            )
        except Http404:
            return {}
        return {credits.code: credits.credits_acquis_de_progression for credits in credits_acquis}

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            'formulaire': self.formulaire_inscriptions_cours,
            'formulaire_hors_programme': self.formulaire_inscription_hors_programme,
            'inscriptions_hors_programmes': self.inscriptions_hors_programme,
            'a_des_mini_formations_inscriptibles': self.a_des_mini_formations_inscriptibles,
            'form': self.formulaire_demande_particuliere,
            'est_annee_paire': self.annee_academique % 2 == 0,
            'demande_particuliere': self.demande_particuliere,
            'est_en_premiere_annee_de_bachelier': "11BA" in self.sigle_formation,
            'a_un_complement': self.a_un_complement_de_formation,
            'credits_acquis_de_progression_par_code': self.credits_acquis_dans_mini_formations,
            'credits_formation': self.credits_formation,
            'has_errors': self.has_errors(),
        }

    @cached_property
    def credits_formation(self) -> int:
        return TrainingService.get_credits(
            person=self.person, year=self.annee_academique, acronym=self.sigle_formation.replace('11BA', '1BA')
        )

    @cached_property
    def a_un_complement_de_formation(self) -> bool:
        return ComplementService.a_un_complement(person=self.person, code_programme=self.code_programme)

    @cached_property
    def demande_particuliere(self) -> Optional['DemandeParticuliere']:
        try:
            return DemandeParticuliereService().recuperer(self.person, self.code_programme)
        except ServiceException:
            return None

    @cached_property
    def formulaire_demande_particuliere(self) -> 'DemandeParticuliereForm':
        initial = {}
        if self.demande_particuliere:
            initial = {'demande_particuliere': self.demande_particuliere.demande}
        return DemandeParticuliereForm(initial=initial)

    def has_errors(self):
        return bool([m.message for m in messages.get_messages(self.request) if m.level == messages.ERROR])
