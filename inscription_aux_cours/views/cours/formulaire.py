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
from typing import List, Optional, Dict

import attr
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.utils.functional import cached_property
from django.views.generic import FormView, TemplateView
from osis_inscription_cours_sdk.model.configuration_formulaire_inscription_cours import \
    ConfigurationFormulaireInscriptionCours
from osis_inscription_cours_sdk.model.demande_particuliere import DemandeParticuliere
from osis_inscription_cours_sdk.model.programme_annuel_etudiant import ProgrammeAnnuelEtudiant
from osis_learning_unit_sdk.model.classe import Classe
from osis_learning_unit_sdk.model.learning_unit import LearningUnit

from base.services.utils import ServiceException
from base.utils.string_utils import unaccent
from inscription_aux_cours.forms.cours.demande_particuliere import DemandeParticuliereForm
from inscription_aux_cours.forms.cours.inscription_hors_programme import InscriptionHorsProgrammeForm
from inscription_aux_cours.services.cours import CoursService
from inscription_aux_cours.services.demande_particuliere import DemandeParticuliereService
from inscription_aux_cours.services.formulaire_inscription import FormulaireInscriptionService
from inscription_aux_cours.services.mini_formation import MiniFormationService
from inscription_aux_cours.views.common import InscriptionAuxCoursViewMixin
from learning_unit.services.classe import ClasseService
from learning_unit.services.learning_unit import LearningUnitService


@attr.dataclass(frozen=True, slots=True, auto_attribs=True)
class InscriptionAUnCoursHorsProgramme:
    code_mini_formation: str
    code_cours: str
    intitule_cours: str
    credits: Decimal


class FormulaireInscriptionAuxCoursView(LoginRequiredMixin,  InscriptionAuxCoursViewMixin, TemplateView):
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
            if formulaire_mini_formation.configuration.autorise_etudiant_a_ajouter_cours
        ]
        choix_mini_formations.sort(key=lambda choix: unaccent(choix[1]))
        if self.formulaire_inscriptions_cours.formulaire_tronc_commun.configuration.autorise_etudiant_a_ajouter_cours:
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
                code_mini_formation="",
                code_cours=inscription.code,
                intitule_cours="",
                credits=inscription.credits
            )
            for inscription
            in self.formulaire_inscriptions_cours["formulaire_tronc_commun"]['inscriptions_hors_programme']
        ]
        for inscriptions_pour_mini_formation in self.formulaire_inscriptions_cours["formulaires_mini_formation"]:
            result += [
                InscriptionAUnCoursHorsProgramme(
                    code_mini_formation=inscriptions_pour_mini_formation.code_programme,
                    code_cours=inscription.code,
                    intitule_cours="",
                    credits=inscription.credits
                ) for inscription in inscriptions_pour_mini_formation['inscriptions_hors_programme']
            ]
        return self._remplir_intitule_cours(result)

    def _remplir_intitule_cours(
            self,
            inscriptions_hors_programme: List['InscriptionAUnCoursHorsProgramme']
    ) -> List['InscriptionAUnCoursHorsProgramme']:
        if not inscriptions_hors_programme:
            return []
        codes_cours = [cours.code_cours for cours in inscriptions_hors_programme]
        unites_enseignements_par_code = self._rechercher_unites_enseignements(codes_cours)
        classes_par_code = self._rechercher_classes(codes_cours)

        return [
            attr.evolve(
                inscription,
                intitule_cours=unites_enseignements_par_code[inscription.code_cours]
                if unites_enseignements_par_code.get(inscription.code_cours)
                else classes_par_code[inscription.code_cours]['intitule']
            )
            for inscription in inscriptions_hors_programme
        ]

    def _rechercher_unites_enseignements(self, codes_cours: List[str]) -> Dict[str, 'str']:
        result = dict()
        for code in codes_cours:
            result[code] = LearningUnitService.get_learning_unit_title(
                year=self.annee_academique,
                acronym=code,
                person=self.person
            )
        return result

    def _rechercher_classes(self, codes_classes: List[str]) -> Dict[str, 'Classe']:
        classes = ClasseService().rechercher_classes(
            self.person,
            annee=self.annee_academique,
            codes=codes_classes
        )
        return {classe['code']: classe for classe in classes}

    @cached_property
    def a_des_mini_formations_inscriptibles(self) -> bool:
        return bool(MiniFormationService().get_inscriptibles(self.person, self.code_programme).mini_formations)

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            'configuration': self.formulaire_inscriptions_cours.formulaire_tronc_commun.configuration,
            'formulaire': self.formulaire_inscriptions_cours,
            'formulaire_hors_programme': self.formulaire_inscription_hors_programme,
            'inscriptions_hors_programmes': self.inscriptions_hors_programme,
            'a_des_mini_formations_inscriptibles': self.a_des_mini_formations_inscriptibles,
            'form': self.formulaire_demande_particuliere,
        }

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
