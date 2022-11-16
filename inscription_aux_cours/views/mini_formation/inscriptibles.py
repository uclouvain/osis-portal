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
from typing import List

from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.utils.functional import cached_property
from django.views.generic import TemplateView
from osis_inscription_cours_sdk.model.inscription_mini_formation import InscriptionMiniFormation
from osis_inscription_cours_sdk.model.liste_mini_formations import ListeMiniFormations

from inscription_aux_cours.services.mini_formation import MiniFormationService
from inscription_aux_cours.views.common import InscriptionAuxCoursViewMixin


class MiniFormationsInscriptiblesView(LoginRequiredMixin, InscriptionAuxCoursViewMixin, TemplateView):
    name = 'mini-formations-inscriptibles'

    # TemplateView
    template_name = "inscription_aux_cours/mini_formation/inscriptibles.html"

    @cached_property
    def mini_formations_inscriptibles(self) -> 'ListeMiniFormations':
        return MiniFormationService().get_mini_formations_inscriptibles(
            self.person,
            self.sigle_formation
        )

    @cached_property
    def inscriptions_mini_formations(self) -> List['InscriptionMiniFormation']:
        return MiniFormationService().get_inscriptions(self.person, self.sigle_formation)

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            'liste_mini_formations_inscriptibles': self.mini_formations_inscriptibles,
            'inscriptions_mini_formations': self.inscriptions_mini_formations,
        }

    def get_success_url(self):
        return reverse("inscription-aux-cours:inscrire-cours", kwargs={"sigle_formation": self.sigle_formation})
