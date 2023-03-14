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
from typing import List, Optional, Dict

from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView
from osis_inscription_cours_sdk.model.demande_particuliere import DemandeParticuliere
from osis_inscription_cours_sdk.model.inscription_cours import InscriptionCours
from osis_program_management_sdk.model.programme import Programme

from base.services.utils import ServiceException
from inscription_aux_cours import formatter
from inscription_aux_cours.data.proposition_programme_annuel import Inscription, InscriptionsParContexte, \
    PropositionProgrammeAnnuel
from inscription_aux_cours.formatter import get_intitule_programme
from inscription_aux_cours.services.cours import CoursService
from inscription_aux_cours.services.demande_particuliere import DemandeParticuliereService
from inscription_aux_cours.views.common import InscriptionAuxCoursViewMixin
from learning_unit.services.classe import ClasseService
from learning_unit.services.learning_unit import LearningUnitService
from program_management.services.programme import ProgrammeService


class RecapitulatifView(LoginRequiredMixin, InscriptionAuxCoursViewMixin, TemplateView):
    name = "recapitulatif"

    template_name = "inscription_aux_cours/cours/recapitulatif.html"

    @cached_property
    def inscriptions(self) -> List['InscriptionCours']:
        return CoursService().recuperer_inscription_cours(self.person, self.code_programme)

    @property
    def codes_cours_du_programme_annuel(self) -> List[str]:
        return [inscription.code_cours for inscription in self.inscriptions]

    @cached_property
    def details_unites_enseignement(self):
        result = LearningUnitService.search_learning_units(
            self.person,
            year=self.annee_academique,
            learning_unit_codes=self.codes_cours_du_programme_annuel
        )
        return {learning_unit['acronym']: learning_unit for learning_unit in result}

    @cached_property
    def cours_dont_prerequis_non_acquis(self) -> List['str']:
        prerequis_non_acquis = CoursService().recuperer_prerequis_non_acquis(self.person, self.code_programme)
        return [prerequis.code_cours for prerequis in prerequis_non_acquis]

    @cached_property
    def details_classes(self):
        result = ClasseService.rechercher_classes(
            self.person,
            annee=self.annee_academique,
            codes=self.codes_cours_du_programme_annuel
        )
        return {classe['code']: classe for classe in result}

    @cached_property
    def details_mini_formation(self) -> Dict[str, 'Programme']:
        codes_mini_formation = set(
            [inscription.code_mini_formation for inscription in self.inscriptions if inscription.code_mini_formation]
        )
        result = ProgrammeService().rechercher(self.person, annee=self.annee_academique, codes=list(codes_mini_formation))
        return {mini_formation.code: mini_formation for mini_formation in result}

    @cached_property
    def programme_annuel_avec_details_cours(self) -> 'PropositionProgrammeAnnuel':
        inscriptions_groupees_par_contexte = itertools.groupby(
            sorted(
                self.inscriptions,
                key=lambda inscr: (inscr.code_mini_formation, inscr.partenariat, inscr.code_cours)
            ), key=lambda inscr: (inscr.code_mini_formation, inscr.partenariat)
        )

        inscriptions_par_contexte = []
        for key, inscriptions in inscriptions_groupees_par_contexte:
            code_mini_formation, partenariat = key
            if code_mini_formation:
                intitule = get_intitule_programme(self.details_mini_formation[code_mini_formation])
            elif partenariat:
                intitule = self._format_intitule_partenariat(partenariat)
            else:
                intitule = formatter.get_intitule_programme(self.programme)
            inscriptions_par_contexte.append(
                InscriptionsParContexte(
                    intitule=intitule,
                    cours=self._build_cours(inscriptions)
                )
            )
        return PropositionProgrammeAnnuel(
            inscriptions_par_contexte=inscriptions_par_contexte
        )

    def _format_intitule_partenariat(self, intitule: str) -> str:
        return str(_('My exchange programme')) + ": " + intitule

    def _build_cours(self, cours_par_contexte) -> List['Inscription']:
        result = []
        for cours in cours_par_contexte:
            code = cours.code_cours
            inscription = Inscription(
                code=code,
                credits=cours['credits'],
                intitule=self._get_intitule(code)
            )
            result.append(inscription)
        return result

    def _get_intitule(self, code) -> str:
        if code in self.details_unites_enseignement:
            return self.details_unites_enseignement[code]['title']
        elif code in self.details_classes:
            return self.details_classes[code]['intitule']
        return LearningUnitService.get_learning_unit_title(
            year=self.annee_academique,
            acronym=code,
            person=self.person
        )

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
            'demande_particuliere': self.demande_particuliere,
            'cours_dont_prerequis_non_acquis': self.cours_dont_prerequis_non_acquis
        }
