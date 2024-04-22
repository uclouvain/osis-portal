##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2024 Université catholique de Louvain (http://www.uclouvain.be)
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
import json
from typing import List, Dict

from osis_inscription_evaluation_sdk.model.formation import Formation
from osis_inscription_evaluation_sdk.model.mon_formulaire_inscription_evaluations import \
    MonFormulaireInscriptionEvaluations
from osis_inscription_evaluation_sdk.model.session_de_travail import SessionDeTravail
from osis_inscription_evaluation_sdk.model.etudiant import Etudiant
from osis_inscription_evaluation_sdk.model.contact_faculte import ContactFaculte
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.utils.functional import cached_property
from django.shortcuts import redirect
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from base.services.utils import ServiceException
from inscription_evaluation.services.formulaire_inscription import FormulaireInscriptionService
from inscription_evaluation.views.common import InscriptionEvaluationViewMixin


class FormulaireInscriptionView(LoginRequiredMixin, InscriptionEvaluationViewMixin, TemplateView):
    name = 'formulaire-inscription'

    # TemplateView
    template_name = "inscription_evaluation/formulaire_inscription.html"

    @cached_property
    def session_de_travail(self) -> 'SessionDeTravail':
        return self.formulaire.session_de_travail

    @cached_property
    def etudiant(self) -> 'Etudiant':
        return self.formulaire.etudiant

    @cached_property
    def formation(self) -> 'Formation':
        return self.formulaire.formation

    @cached_property
    def contact_faculte(self) -> 'ContactFaculte':
        return self.formulaire.contact_faculte

    @cached_property
    def inscriptions(self) -> List[Dict]:
        return self.formulaire.inscriptions

    @cached_property
    def peut_s_inscrire_a_minimum_une_evaluation(self) -> bool:
        return any(inscription['peut_inscrire_evaluation'] for inscription in self.inscriptions)

    @cached_property
    def formulaire(self) -> 'MonFormulaireInscriptionEvaluations':
        formulaire = FormulaireInscriptionService().recuperer(self.person, self.sigle_formation)
        FormulaireInscriptionService().marquer_comme_lu(self.person, self.sigle_formation)
        return formulaire

    @cached_property
    def group_inscriptions_by_contexte_inscription(self) -> Dict[str, List[Dict]]:
        result = {}
        for insc in self.inscriptions:
            result.setdefault(insc['contexte_inscription'], []).append(insc)
        return result

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            'session_de_travail': self.session_de_travail,
            'etudiant': self.etudiant,
            'formation': self.formation,
            'contact_faculte': self.contact_faculte,
            'a_des_inscriptions': bool(self.inscriptions),
            'map_insc_eval_par_contexte': self.group_inscriptions_by_contexte_inscription,
            'peut_s_inscrire_a_minimum_une_evaluation': self.peut_s_inscrire_a_minimum_une_evaluation,
        }

    def post(self, request, *args, **kwargs):
        erreurs = []
        try:
            FormulaireInscriptionService.soumettre(
                person=self.person,
                sigle_formation=self.sigle_formation,
                demandes_inscriptions=json.loads(self.request.POST.get('demandes_inscriptions')),
                demandes_desinscriptions=json.loads(self.request.POST.get('demandes_desinscriptions')),
            )
        except ServiceException as e:
            erreurs = e.messages
        self.afficher_erreurs(erreurs)
        if erreurs:
            messages.add_message(
                self.request,
                messages.ERROR,
                str(_("Your request to register for evaluations has not been saved.")),
            )
            messages.add_message(
                self.request,
                messages.ERROR,
                str(_(
                    "Please correct any errors in your form to save it and continue "
                    "to the summary of your evaluation application."
                )),
            )
            return redirect('inscription-evaluation:formulaire-inscription', **self.kwargs)
        return redirect('inscription-evaluation:recapitulatif', **self.kwargs)

    def afficher_erreurs(self, erreurs: List[str]) -> None:
        for erreur in erreurs:
            messages.add_message(self.request, messages.ERROR, erreur)
