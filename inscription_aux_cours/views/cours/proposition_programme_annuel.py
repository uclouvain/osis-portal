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
from typing import Optional, List

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
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

    @property
    def codes_cours(self) -> List[str]:
        return [c for c in self.request.POST.getlist('cours', []) if c]

    def post(self, request, *args, **kwargs):
        erreurs = []

        inscriptions = {
            k.replace('unite_enseignement_inscriptible_', '')
            for k in request.POST.keys() if 'unite_enseignement_inscriptible_' in k
        }
        inscriptions_tronc_commun = []
        insc_par_mini_formation = {}
        for i in inscriptions:
            code_mini_formation, code_ue = i.split('_')
            if not code_mini_formation:
                inscriptions_tronc_commun.append(code_ue)
            else:
                insc_par_mini_formation.setdefault(code_mini_formation, []).append(code_ue)

        demandes_particulieres_dans_tronc_commun = []
        demandes_particulieres_dans_mini_formation = {}
        if self.code_mini_formation:
            demandes_particulieres_dans_mini_formation[self.code_mini_formation] = self.codes_cours
        else:
            demandes_particulieres_dans_tronc_commun = self.codes_cours

        demande_particuliere = request.POST['demande_particuliere']

        # TODO :: utiliser les Forms pour sécurité (injection SQL, etc)

        try:
            FormulaireInscriptionService.enregistrer_formulaire_proposition_pae(
                person=self.person,
                code_programme=self.code_programme,
                inscriptions_tronc_commun=inscriptions_tronc_commun,
                inscriptions_dans_mini_formations=insc_par_mini_formation,
                demandes_particulieres_dans_tronc_commun=demandes_particulieres_dans_tronc_commun,
                demandes_particulieres_dans_mini_formation=demandes_particulieres_dans_mini_formation,
                demande_particuliere=demande_particuliere,
            )
        except ServiceException as e:
            erreurs = e.messages

        self.afficher_erreurs(erreurs)

        return redirect('inscription-aux-cours:recapitulatif', code_programme=self.code_programme)

    def afficher_erreurs(self, erreurs: List[str]) -> None:
        for erreur in erreurs:
            messages.add_message(self.request, messages.ERROR, erreur)
