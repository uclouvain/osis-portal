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

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.utils.functional import cached_property
from django.views.generic import TemplateView
from osis_offer_enrollment_sdk.model.inscription import Inscription
from osis_program_management_sdk.model.programme import Programme

from base.business.student import find_by_user_and_discriminate
from base.models.person import Person
from base.models.student import Student
from base.services.offer_enrollment import InscriptionFormationsService
from inscription_aux_cours.services.periode import PeriodeInscriptionAuxCoursService
from program_management.services.programme import ProgrammeService


class SelectionnerFormationView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    permission_required = "base.is_student"

    template_name = 'inscription_aux_cours/selectionner_formation.html'

    name = 'selectionner-formation'

    @cached_property
    def person(self) -> 'Person':
        return Person.objects.get(user=self.request.user)

    @cached_property
    def student(self) -> 'Student':
        return find_by_user_and_discriminate(self.request.user)

    @cached_property
    def annee_academique(self) -> 'int':
        return PeriodeInscriptionAuxCoursService().get_annee(self.person)

    @cached_property
    def inscriptions(self) -> List['Inscription']:
        return InscriptionFormationsService.mes_inscriptions(self.person, annee=self.annee_academique)

    @cached_property
    def programmes(self) -> List['Programme']:
        if not self.inscriptions:
            return []
        codes = [inscription.code_programme for inscription in self.inscriptions]
        return ProgrammeService.rechercher(self.person, annee=self.annee_academique, codes=codes)

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            'student': self.student,
            'programmes': self.programmes,
            'annee_academique': self.annee_academique,
        }
