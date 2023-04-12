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
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
from django.views.generic import FormView

from inscription_aux_cours.forms.cours.demande_particuliere import DemandeParticuliereForm
from inscription_aux_cours.services.demande_particuliere import DemandeParticuliereService
from inscription_aux_cours.views.common import InscriptionAuxCoursViewMixin


@method_decorator(require_POST, name='dispatch')
class DemandeParticuliereView(LoginRequiredMixin, InscriptionAuxCoursViewMixin, FormView):
    name = "demande-particuliere"
    form_class = DemandeParticuliereForm

    def form_valid(self, form: 'DemandeParticuliereForm'):
        demande_particuliere = form.cleaned_data['demande_particuliere']
        if demande_particuliere:
            self._effectuer_une_demande_particuliere(demande_particuliere)
        else:
            self._retirer_demande_particuliere()

        return HttpResponse()

    def _effectuer_une_demande_particuliere(self, demande_particuliere) -> None:
        DemandeParticuliereService.effectuer(self.person, self.code_programme, demande_particuliere)

    def _retirer_demande_particuliere(self) -> None:
        DemandeParticuliereService.retirer(self.person, self.code_programme)
