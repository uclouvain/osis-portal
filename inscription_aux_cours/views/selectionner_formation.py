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
from typing import List, Dict

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.utils.functional import cached_property
from django.views.generic import TemplateView
from osis_inscription_cours_sdk.model.autorise_inscrire_aux_cours import AutoriseInscrireAuxCours
from osis_offer_enrollment_sdk.model.inscription import Inscription
from osis_program_management_sdk.model.programme import Programme

from base.models.person import Person
from base.services.offer_enrollment import InscriptionFormationsService
from inscription_aux_cours.services.autorisation import AutorisationService
from inscription_aux_cours.services.periode import PeriodeInscriptionAuxCoursService
from inscription_aux_cours.services.periode_pour_etudiant_inscrire_aux_cours import PeriodeInscriptionEtudiantService
from inscription_aux_cours.views.common import recuperer_programmes


class SelectionnerFormationView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    permission_required = "base.is_student"

    template_name = 'inscription_aux_cours/selectionner_formation.html'

    name = 'selectionner-formation'

    @cached_property
    def person(self) -> 'Person':
        return Person.objects.get(user=self.request.user)

    @cached_property
    def annee_academique(self) -> 'int':
        return PeriodeInscriptionAuxCoursService().get_annee(self.person)

    @cached_property
    def inscriptions(self) -> List['Inscription']:
        return InscriptionFormationsService.mes_inscriptions(self.person, annee=self.annee_academique)

    @property
    def noma(self) -> str:
        return self.inscriptions[0].noma if self.inscriptions else ""

    @cached_property
    def programmes(self) -> List['Programme']:
        return recuperer_programmes(self.person, self.annee_academique, self.inscriptions) if self.inscriptions else []

    @cached_property
    def autorisations(self) -> Dict[str, 'AutoriseInscrireAuxCours']:
        return {
            programme.code: AutorisationService().est_autorise(self.person, programme.code)
            for programme in self.programmes
        }

    @cached_property
    def periodes(self) -> Dict[str, 'AutoriseInscrireAuxCours']:
        return {
            programme.code: PeriodeInscriptionEtudiantService().get_periode(self.person, programme.code)
            for programme in self.programmes
        }

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            'person': self.person,
            'noma': self.noma,
            'programmes': self.programmes,
            'autorisations': self.autorisations,
            'periodes': self.periodes,
            'annee_academique': self.annee_academique,
        }
