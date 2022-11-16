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
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.functional import cached_property
from django.views.generic import TemplateView
from osis_education_group_sdk.model.training_detailed import TrainingDetailed
from osis_inscription_cours_sdk.model.autorise_inscrire_aux_cours import AutoriseInscrireAuxCours

from base.business.student import find_by_user_and_discriminate
from base.models import academic_year
from base.models.person import Person
from base.models.student import Student
from education_group.services.training import TrainingService
from inscription_aux_cours.services.autorisation import AutorisationService


class InscriptionNonAutoriseeView(LoginRequiredMixin, TemplateView):
    name = 'non-autorisee'
    template_name = "inscription_aux_cours/non_autorisee.html"

    @cached_property
    def person(self) -> 'Person':
        return Person.objects.get(user=self.request.user)

    @cached_property
    def student(self) -> 'Student':
        return find_by_user_and_discriminate(self.request.user)

    @property
    def sigle_formation(self) -> str:
        return self.kwargs['sigle_formation']

    @cached_property
    def annee_academique(self) -> 'int':
        return academic_year.starting_academic_year().year

    @cached_property
    def formation(self) -> 'TrainingDetailed':
        return TrainingService().get_detail(self.person, self.annee_academique, self.sigle_formation)

    @cached_property
    def autorisation(self) -> 'AutoriseInscrireAuxCours':
        return AutorisationService().est_autorise(self.person, self.sigle_formation)

    def get(self, request, *args, **kwargs):
        if self.autorisation.autorise:
            return redirect(reverse('inscription-aux-cours:selectionner-formation'))
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            "raison": self.autorisation.msg,
            'student': self.student,
            'formation': self.formation,
            'annee_academique': self.annee_academique,
        }
