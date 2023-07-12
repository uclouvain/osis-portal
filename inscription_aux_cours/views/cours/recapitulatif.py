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
from typing import List, Optional, Dict

from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView
from osis_inscription_cours_sdk.model.activites_aide_reussite import ActivitesAideReussite
from osis_inscription_cours_sdk.model.demande_particuliere import DemandeParticuliere
from osis_inscription_cours_sdk.model.programme_annuel_etudiant import ProgrammeAnnuelEtudiant
from osis_program_management_sdk.model.programme import Programme

from base.services.utils import ServiceException
from base.utils.string_utils import unaccent
from education_group.services.training import TrainingService
from inscription_aux_cours import formatter
from inscription_aux_cours.data.proposition_programme_annuel import (
    Inscription,
    InscriptionsParContexte,
    PropositionProgrammeAnnuel,
)
from inscription_aux_cours.formatter import get_intitule_programme
from inscription_aux_cours.services.activites_aide_reussite import ActivitesAideReussiteService
from inscription_aux_cours.services.code_unite_enseignement import CodeParser
from inscription_aux_cours.services.complement import ComplementService
from inscription_aux_cours.services.cours import CoursService
from inscription_aux_cours.services.demande_particuliere import DemandeParticuliereService
from inscription_aux_cours.services.proprietes_pae import ProprietesPAEService
from inscription_aux_cours.views.common import CompositionPAEViewMixin
from learning_unit.services.classe import ClasseService
from program_management.services.programme import ProgrammeService


class RecapitulatifView(LoginRequiredMixin, CompositionPAEViewMixin, TemplateView):
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

    @property
    def codes_cours_des_partenariats(self) -> List[str]:
        return [
            cours['code'] for partenariat in self.programme_annuel['partenariats'] for cours in partenariat['cours']
        ]

    @cached_property
    def details_classes(self):
        result = ClasseService.rechercher_classes(
            self.person, annee=self.annee_academique, codes=self.codes_cours_du_programme_annuel
        )
        return {classe['code']: classe for classe in result}

    @cached_property
    def details_mini_formation(self) -> Dict[str, 'Programme']:
        codes_mini_formation = [mini_formation['code'] for mini_formation in self.programme_annuel['mini_formations']]
        result = ProgrammeService().rechercher(self.person, annee=self.annee_academique, codes=codes_mini_formation)
        return {mini_formation.code: mini_formation for mini_formation in result}

    @cached_property
    def programme_annuel_avec_details_cours(self) -> 'PropositionProgrammeAnnuel':
        intitule_par_code = self.recuperer_intitules_unites_enseignement(
            self.codes_cours_du_programme_annuel + self.codes_cours_des_partenariats,
        )

        inscriptions_tronc_commun = InscriptionsParContexte(
            intitule=formatter.get_intitule_programme(self.programme),
            cours=self._build_cours(self.programme_annuel['tronc_commun'], intitule_par_code),
        )

        inscriptions_aux_mini_formations = [
            InscriptionsParContexte(
                intitule=get_intitule_programme(self.details_mini_formation[mini_formation['code']]),
                cours=self._build_cours(mini_formation['cours'], intitule_par_code),
            )
            for mini_formation in self.programme_annuel['mini_formations']
        ]
        inscriptions_aux_mini_formations.sort(key=lambda contexte: unaccent(contexte.intitule))

        inscriptions_aux_partenariats = [
            InscriptionsParContexte(
                intitule=self._format_intitule_partenariat(partenariat['intitule']),
                cours=self._build_cours(partenariat['cours'], intitule_par_code),
            )
            for partenariat in self.programme_annuel['partenariats']
        ]
        inscriptions_aux_partenariats.sort(key=lambda contexte: unaccent(contexte.intitule))

        inscriptions = [inscriptions_tronc_commun] if inscriptions_tronc_commun.cours else []
        inscriptions += inscriptions_aux_mini_formations
        inscriptions += inscriptions_aux_partenariats

        return PropositionProgrammeAnnuel(inscriptions_par_contexte=inscriptions)

    def _format_intitule_partenariat(self, intitule: str) -> str:
        return str(_('My exchange programme')) + ": " + intitule

    def _build_cours(self, cours_par_contexte, intitule_par_code) -> List['Inscription']:
        result = []
        for cours in cours_par_contexte:
            code = cours['code']
            inscription = Inscription(
                code=code,
                credits=cours['credits'],
                intitule=self._get_intitule(code, intitule_par_code),
            )
            result.append(inscription)
        return result

    def _get_intitule(self, code, intitule_par_code) -> str:
        if code in self.details_classes:
            return self.details_classes[code]['intitule']
        return intitule_par_code.get(code, '')

    @cached_property
    def demande_particuliere(self) -> Optional['DemandeParticuliere']:
        try:
            return DemandeParticuliereService().recuperer(self.person, self.code_programme)
        except ServiceException:
            return None

    @cached_property
    def activites_aide_reussite(self) -> Optional['ActivitesAideReussite']:
        try:
            return ActivitesAideReussiteService.get_activites_aide_reussite(self.person, self.code_programme)
        except ServiceException:
            return None

    @cached_property
    def a_un_complement_de_formation(self) -> bool:
        return ComplementService.a_un_complement(person=self.person, code_programme=self.code_programme)

    @cached_property
    def credits_formation(self) -> int:
        return TrainingService.get_credits(
            person=self.person, year=self.annee_academique, acronym=self.sigle_formation.replace('11BA', '1BA')
        )

    def get_context_data(self, **kwargs):
        a_une_condition_bama15_ou_1adp = ProprietesPAEService.a_une_condition_bama15_ou_1adp(
            self.person,
            self.sigle_formation.replace('11BA', '1BA')
        )
        maximum_credits_inscrits_autorises = 60 if a_une_condition_bama15_ou_1adp else 90
        depasse_le_maximum_credits_inscrits = \
            self.programme_annuel_avec_details_cours.total_credits > maximum_credits_inscrits_autorises
        ue_avec_prerequis = CoursService().recuperer_unites_enseignement_avec_prerequis(
            self.person,
            self.code_programme,
        )
        codes_inscrits = self.programme_annuel_avec_details_cours.codes_inscrits
        codes_ue_sans_classe_inscrits = {CodeParser.get_code_unite_enseignement(code) for code in codes_inscrits}
        cours_dont_prerequis_non_acquis = {
            ue.code: ue for ue in ue_avec_prerequis
            if not ue.prerequis_sont_acquis and ue.code in codes_ue_sans_classe_inscrits
        }
        codes_dont_prerequis_non_acquis_et_inscrit_a_au_moins_un_prerequis = {
            ue.code for ue in cours_dont_prerequis_non_acquis.values()
            if ue.code in codes_ue_sans_classe_inscrits
            and any((code_inscrit in ue.prerequis_texte for code_inscrit in self.codes_cours_du_programme_annuel))
        }
        est_en_fin_de_cycle = self.programme_annuel.est_en_fin_de_cycle
        return {
            **super().get_context_data(**kwargs),
            'programme_annuel': self.programme_annuel_avec_details_cours,
            'demande_particuliere': self.demande_particuliere,
            'bloquer_soumission': (
                not est_en_fin_de_cycle and codes_dont_prerequis_non_acquis_et_inscrit_a_au_moins_un_prerequis
            ) or (
                depasse_le_maximum_credits_inscrits
            ),
            'cours_dont_prerequis_non_acquis': set(cours_dont_prerequis_non_acquis.keys()),
            'codes_dont_prerequis_non_acquis_et_inscrit_a_au_moins_un_prerequis':
                codes_dont_prerequis_non_acquis_et_inscrit_a_au_moins_un_prerequis,
            'codes_ue_avec_prerequis': {ue.code for ue in ue_avec_prerequis},
            'codes_ue_prerequis_acquis': {ue.code for ue in ue_avec_prerequis if ue.prerequis_sont_acquis},
            'est_en_fin_de_cycle': est_en_fin_de_cycle,
            'activites_aide_reussite': self.activites_aide_reussite,
            'depasse_le_maximum_credits_inscrits': depasse_le_maximum_credits_inscrits,
            'est_en_premiere_annee_de_bachelier': "11BA" in self.sigle_formation,
            'a_un_complement': self.a_un_complement_de_formation,
            'credits_formation': self.credits_formation,
            'a_une_condition_bama15_ou_1adp': a_une_condition_bama15_ou_1adp
        }
