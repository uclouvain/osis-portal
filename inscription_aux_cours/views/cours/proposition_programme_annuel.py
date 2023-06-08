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
from typing import Optional, List, Dict

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.decorators.http import require_POST

from base.services.utils import ServiceException
from inscription_aux_cours.services.formulaire_inscription import FormulaireInscriptionService
from inscription_aux_cours.views.common import CompositionPAEViewMixin
from osis_common.utils.htmx import HtmxMixin


@method_decorator(require_POST, name='dispatch')
class EnregistrerPropositionProgrammeAnnuelView(HtmxMixin, LoginRequiredMixin, CompositionPAEViewMixin, View):
    name = 'enregistrer-proposition-programme-annuel'

    @property
    def code_mini_formation(self) -> Optional[str]:
        return self.request.POST.get('code_mini_formation')

    @cached_property
    def nouvelles_demandes_hors_formulaire(self) -> Dict[str, List[str]]:
        # Demandes via l'autocomplete et le radio bouton
        codes_cours = [c for c in self.request.POST.getlist('cours', []) if c]
        return {self.code_mini_formation: codes_cours}

    @property
    def separateur_demandes(self) -> str:
        return '&'

    def _valider_max_length(self, valeur):
        if len(valeur) > 1000:
            raise ValidationError("Valeur trop grande.")

    def _clean(self, valeur) -> Dict[str, List[str]]:
        """
        Vérifie l'intégrité des inscriptions.
        :param valeur: Chaine de caractère formatée comme suit : CodeMiniFromation,CodeUE&CodeMiniFromation,codeUE2
        :return: Dictionnaire associant le contexte d'inscription (code_mini_formation) à la liste des codes UE
        """
        self._valider_max_length(valeur)
        if not valeur:
            return {}
        taille_max_code = 15
        expressions = valeur.split(self.separateur_demandes)
        result = {}
        for expr in expressions:
            if expr:
                code_mini_formation, code_ue = expr.split(',')
                if len(code_mini_formation) > taille_max_code or len(code_ue) > taille_max_code:
                    raise ValidationError("Données corrompues")
                if code_ue:
                    result.setdefault(code_mini_formation, set()).add(code_ue)
        return {code_mini_form: list(codes) for code_mini_form, codes in result.items()}

    @cached_property
    def commentaire(self) -> str:
        commentaire = self.request.POST['demande_particuliere']
        self._valider_max_length(commentaire)
        return commentaire

    @cached_property
    def demandes_inscriptions_dans_formulaires(self) -> Dict[str, List[str]]:
        # Inclus toutes les demandes inscriptions faites dans les formulaires (pas les demandes hors formulaire)
        return self._clean(self.request.POST['demandes_inscriptions_dans_formulaire'])

    @cached_property
    def demandes_desinscriptions(self) -> List[str]:
        # Inclus les demandes de désinscription hors formulaire et dans formulaire
        demande_par_code_mini_form = self._clean(self.request.POST['demandes_desinscriptions'])
        return [code_ue for codes_ue in demande_par_code_mini_form.values() for code_ue in codes_ue]

    def post(self, request, *args, **kwargs):
        erreurs = []

        tronc_commun = ''
        inscriptions_tronc_commun = self.demandes_inscriptions_dans_formulaires.get(tronc_commun, [])
        inscriptions_dans_mini_formations = {
            code_mini_form: codes_ue for code_mini_form, codes_ue in self.demandes_inscriptions_dans_formulaires.items()
            if code_mini_form != tronc_commun
        }
        demandes_particulieres_dans_tronc_commun = self.nouvelles_demandes_hors_formulaire.get(tronc_commun, [])
        demandes_particulieres_dans_mini_formation = {
            code_mini_form: codes_ue for code_mini_form, codes_ue in self.nouvelles_demandes_hors_formulaire.items()
            if code_mini_form != tronc_commun
        }

        try:
            FormulaireInscriptionService.enregistrer_formulaire_proposition_pae(
                person=self.person,
                code_programme=self.code_programme,
                inscriptions_tronc_commun=inscriptions_tronc_commun,
                inscriptions_dans_mini_formations=inscriptions_dans_mini_formations,
                demandes_particulieres_dans_tronc_commun=demandes_particulieres_dans_tronc_commun,
                demandes_particulieres_dans_mini_formation=demandes_particulieres_dans_mini_formation,
                demandes_desinscriptions=self.demandes_desinscriptions,
                demande_particuliere=self.commentaire,
            )
        except ServiceException as e:
            erreurs = e.messages

        self.afficher_erreurs(erreurs)
        if erreurs:
            messages.add_message(
                self.request,
                messages.ERROR,
                _("Please fix errors to save and continue to the recap of your annual program proposal"),
            )
            return redirect('inscription-aux-cours:formulaire-inscription-cours', **self.kwargs)

        return redirect('inscription-aux-cours:formulaire-activites-aide-reussite', **self.kwargs)

    def afficher_erreurs(self, erreurs: List[str]) -> None:
        for erreur in erreurs:
            messages.add_message(self.request, messages.ERROR, erreur)
