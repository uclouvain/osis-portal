# ##############################################################################
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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
# ##############################################################################
from _decimal import Decimal

from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.functional import cached_property
from django.views.generic import TemplateView
from osis_parcours_interne_sdk.model.progression_de_cycle import ProgressionDeCycle

from base.models.person import Person
from inscription_aux_cours.services.periode import PeriodeInscriptionAuxCoursService
from inscription_aux_cours.services.progression import ProgressionService


class BarreDeProgressionDeCycleView(LoginRequiredMixin, TemplateView):
    name = 'barre-progression-cycle-view'

    # HtmxMixin
    template_name = "inscription_aux_cours/blocks/barre_de_progression.html"

    @cached_property
    def person(self) -> 'Person':
        return Person.objects.get(user=self.request.user)

    @property
    def sigle_programme(self):
        return self.kwargs['sigle_programme']

    @cached_property
    def progression(self) -> 'ProgressionDeCycle':
        return ProgressionService.recuperer_progression_de_cycle(
            person=self.person, sigle_programme=self.sigle_programme.replace('11BA', '1BA')
        )

    @cached_property
    def annee_academique(self) -> 'int':
        return PeriodeInscriptionAuxCoursService().get_annee(self.person)

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            'annee_academique': self.annee_academique,
            'barre_progression_max': self.progression.barre_de_progression_max,
            'credits_acquis': Decimal(self.progression.credits_acquis),
            'credits_inscrits': Decimal(self.progression.credits_inscrits),
            'credits_de_progression_potentielle': self.progression.credits_de_progression_potentielle,
            'credits_cibles': self.progression.credits_cibles,
            'valeur_jalon': self.progression.valeur_jalon,
            'intitule': self.progression.intitule,
            'condition_d_affichage': bool(self.progression.credits_cibles),
        }
