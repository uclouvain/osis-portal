##############################################################################
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
from typing import List

from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.shortcuts import redirect
from django.contrib import messages
from base.services.utils import ServiceException
from django.utils.translation import gettext_lazy as _

from inscription_evaluation.services.formulaire_inscription import FormulaireInscriptionService
from inscription_evaluation.views.common import InscriptionEvaluationViewMixin


@method_decorator(require_POST, name='dispatch')
class EnregistrerDemandeInscriptionView(LoginRequiredMixin, InscriptionEvaluationViewMixin, View):
    name = 'enregistrer-proposition-inscriptions'

    def post(self, request, *args, **kwargs):
        erreurs = []
        try:
            FormulaireInscriptionService.soumettre(
                person=self.person,
                code_programme=self.code_programme,
                demandes_inscriptions=None,
                demandes_desinscriptions=None,
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
