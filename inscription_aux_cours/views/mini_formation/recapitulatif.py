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
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.functional import cached_property
from django.views.generic import TemplateView
from osis_inscription_cours_sdk.model.inscription_mini_formation import InscriptionMiniFormation

from education_group.services.mini_training import MiniTrainingService
from inscription_aux_cours.services.mini_formation import MiniFormationService
from inscription_aux_cours.views.common import InscriptionAuxCoursViewMixin


class RecapitulatifInscriptionsMiniFormationsView(LoginRequiredMixin, InscriptionAuxCoursViewMixin, TemplateView):
    name = "recapitulatif-mini-formations"

    template_name = "inscription_aux_cours/mini_formation/recapitulatif.html"

    @cached_property
    def inscriptions_mini_formations(self) -> List['InscriptionMiniFormation']:
        return MiniFormationService().get_inscriptions(self.person, self.sigle_formation)

    @cached_property
    def details_mini_formations_inscrites(self):
        codes_mini_formation = [
            mini_formation.code_mini_formation
            for mini_formation in self.inscriptions_mini_formations
        ]
        result = MiniTrainingService().search(self.person, year=self.annee_academique, codes=codes_mini_formation)
        return [mini_formation for mini_formation in result]

    def get(self, request, *args, **kwargs):
        if not self.inscriptions_mini_formations:
            return redirect(
                reverse(
                    "inscription-aux-cours:mini-formations-inscriptibles",
                    kwargs={"sigle_formation": self.sigle_formation}
                )
            )
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            'mini_formations': self.details_mini_formations_inscrites,
        }
