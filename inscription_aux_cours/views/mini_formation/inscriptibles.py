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
from osis_education_group_sdk.model.mini_training import MiniTraining
from osis_inscription_cours_sdk.model.inscription_mini_formation import InscriptionMiniFormation
from osis_inscription_cours_sdk.model.liste_mini_formations import ListeMiniFormations

from education_group.services.mini_training import MiniTrainingService
from inscription_aux_cours.services.mini_formation import MiniFormationService
from inscription_aux_cours.views.common import InscriptionAuxCoursViewMixin
from program_management.services.programme import ProgrammeService


class MiniFormationsInscriptiblesView(LoginRequiredMixin, InscriptionAuxCoursViewMixin, TemplateView):
    name = 'mini-formations-inscriptibles'

    # TemplateView
    template_name = "inscription_aux_cours/mini_formation/inscriptibles.html"

    @cached_property
    def liste_mini_formations_inscriptibles(self) -> 'ListeMiniFormations':
        return MiniFormationService().get_inscriptibles(self.person, self.code_programme)

    @cached_property
    def inscriptions(self) -> List['InscriptionMiniFormation']:
        return MiniFormationService().get_inscriptions(self.person, self.code_programme)

    @cached_property
    def mini_formations_inscrites_non_inscriptibles(self) -> List['MiniTraining']:
        if not self.inscriptions:
            return []
        codes_mini_formations_inscrites = {
            inscription.code_mini_formation
            for inscription in self.inscriptions
        }
        codes_mini_formations_inscriptibles = {
            mini_formation.code
            for mini_formation in self.liste_mini_formations_inscriptibles.mini_formations
        }
        codes_mini_formations_inscrites_non_inscriptibles = codes_mini_formations_inscrites - \
            codes_mini_formations_inscriptibles
        return MiniTrainingService().search(
            self.person,
            year=self.annee_academique,
            codes=list(codes_mini_formations_inscrites_non_inscriptibles)
        )

    def get(self, request, *args, **kwargs):
        if not self.liste_mini_formations_inscriptibles.mini_formations:
            return redirect(
                reverse(
                    "inscription-aux-cours:formulaire-inscription-cours",
                    kwargs={"code_programme": self.code_programme}
                )
            )
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            'intitule': self.liste_mini_formations_inscriptibles.intitule,
            'commentaire': self.liste_mini_formations_inscriptibles.commentaire,
            'inscriptibles': self.liste_mini_formations_inscriptibles.mini_formations,
            'inscriptions': self.inscriptions,
            'est_bachelier': ProgrammeService.est_bachelier(self.programme),
            'mini_formations_inscrites_non_inscriptibles': self.mini_formations_inscrites_non_inscriptibles,
        }

    def get_success_url(self):
        return reverse("inscription-aux-cours:inscrire-cours", kwargs={"code_programme": self.code_programme})
