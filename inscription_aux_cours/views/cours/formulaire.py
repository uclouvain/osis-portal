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
import itertools
from decimal import Decimal
from typing import List, Optional, Dict

import attr
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.utils.functional import cached_property
from django.views.generic import FormView
from osis_inscription_cours_sdk.model.configuration_formulaire_inscription_cours import \
    ConfigurationFormulaireInscriptionCours
from osis_inscription_cours_sdk.model.demande_particuliere import DemandeParticuliere
from osis_inscription_cours_sdk.model.programme_annuel_etudiant import ProgrammeAnnuelEtudiant
from osis_learning_unit_sdk.model.classe import Classe
from osis_learning_unit_sdk.model.learning_unit import LearningUnit

from inscription_aux_cours.forms.cours.demande_particuliere import DemandeParticuliereForm
from inscription_aux_cours.forms.cours.inscription_hors_programme import InscriptionHorsProgrammeForm
from inscription_aux_cours.services.cours import CoursService
from inscription_aux_cours.services.demande_particuliere import DemandeParticuliereService
from inscription_aux_cours.services.formulaire_inscription import FormulaireInscriptionService
from inscription_aux_cours.views.common import InscriptionAuxCoursViewMixin
from learning_unit.services.classe import ClasseService
from learning_unit.services.learning_unit import LearningUnitService


@attr.dataclass(frozen=True, slots=True, auto_attribs=True)
class InscriptionAUnCoursHorsProgramme:
    code_mini_formation: str
    code_cours: str
    intitule_cours: str
    credits: Decimal


class FormulaireInscriptionAuxCoursView(LoginRequiredMixin,  InscriptionAuxCoursViewMixin, FormView):
    name = 'formulaire-inscription-cours'

    # TemplateView
    template_name = "inscription_aux_cours/cours/formulaire.html"
    form_class = DemandeParticuliereForm

    @cached_property
    def formulaire_inscriptions_cours(self):
        return FormulaireInscriptionService().recuperer(self.person, self.annee_academique, self.sigle_formation)

    @cached_property
    def configuration_formulaire(self) -> 'ConfigurationFormulaireInscriptionCours':
        return FormulaireInscriptionService().recuperer_configuration(
            self.person,
            self.annee_academique,
            self.sigle_formation
        )

    @cached_property
    def formulaire_inscription_hors_programme(self) -> 'InscriptionHorsProgrammeForm':
        mini_formations = [('', self.formation.title)]
        mini_formations += [
            (mini_formation.code_programme, mini_formation.intitule_formation)
            for mini_formation in self.formulaire_inscriptions_cours.formulaires_mini_formation
        ]
        return InscriptionHorsProgrammeForm(
            mini_formations,
            initial={'annee': self.annee_academique},
        )

    @cached_property
    def programme_annuel_etudiant(self) -> 'ProgrammeAnnuelEtudiant':
        return CoursService().recuperer_inscriptions(self.person, self.annee_academique, self.sigle_formation)

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
        codes_cours = [cours.code_cours for cours in inscriptions_hors_programme]
        unites_enseignements_par_code = self._rechercher_unites_enseignements(codes_cours)
        classes_par_code = self._rechercher_classes(codes_cours)

        return [
            attr.evolve(
                inscription,
                intitule_cours=unites_enseignements_par_code[inscription.code_cours]['title']
                if unites_enseignements_par_code.get(inscription.code_cours)
                else classes_par_code[inscription.code_cours]['intitule']
            )
            for inscription in inscriptions_hors_programme
        ]

    def _rechercher_unites_enseignements(self, codes_cours: List[str]) -> Dict[str, 'LearningUnit']:
        unites_enseignements = LearningUnitService().search_learning_units(
            self.person,
            year=self.annee_academique,
            learning_unit_codes=codes_cours
        )
        return {unites_enseignement['acronym']: unites_enseignement for unites_enseignement in unites_enseignements}

    def _rechercher_classes(self, codes_classes: List[str]) -> Dict[str, 'Classe']:
        classes = ClasseService().rechercher_classes(
            self.person,
            annee=self.annee_academique,
            codes=codes_classes
        )
        return {classe['code']: classe for classe in classes}

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            'configuration': self.configuration_formulaire,
            'formulaire': self.formulaire_inscriptions_cours,
            'formulaire_hors_programme': self.formulaire_inscription_hors_programme,
            'inscriptions_hors_programmes': self.inscriptions_hors_programme,
        }

    @cached_property
    def demande_particuliere(self) -> Optional['DemandeParticuliere']:
        return DemandeParticuliereService().recuperer(self.person, self.annee_academique, self.sigle_formation)

    def get_initial(self):
        initial = super().get_initial()
        if self.demande_particuliere:
            initial['demande_particuliere'] = self.demande_particuliere.demande
        return initial

    def form_valid(self, form: 'DemandeParticuliereForm'):
        demande = form.cleaned_data['demande_particuliere']
        if not form.has_changed():
            return super().form_valid(form)

        if demande:
            DemandeParticuliereService().effectuer(self.person, self.annee_academique, self.sigle_formation, demande)
        else:
            DemandeParticuliereService().retirer(self.person, self.annee_academique, self.sigle_formation)

        return super().form_valid(form)

    def get_success_url(self):
        return reverse("inscription-aux-cours:recapitulatif", kwargs={"sigle_formation": self.sigle_formation})
