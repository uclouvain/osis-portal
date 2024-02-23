##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2024 Université catholique de Louvain (http://www.uclouvain.be)
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
from django.http import Http404
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.functional import cached_property
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.utils.translation import gettext_lazy as _


from osis_inscription_evaluation_sdk.model.mes_formations import MesFormations
from osis_inscription_evaluation_sdk.model.etudiant import Etudiant
from osis_inscription_evaluation_sdk.model.inscription_formation import InscriptionFormation

from base.models.person import Person
from continuing_education.views.common import display_error_messages
from inscription_evaluation.services.mes_programmes import MesProgrammesService
from inscription_evaluation.services.periode import PeriodeInscriptionAuxEvaluationsService


class SelectionnerProgrammeView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    permission_required = "base.is_student"

    template_name = 'inscription_evaluation/selectionner_programme.html'

    name = 'selectionner-programme'

    @cached_property
    def person(self) -> 'Person':
        return Person.objects.get(user=self.request.user)

    @cached_property
    def annee_academique(self) -> 'int':
        return PeriodeInscriptionAuxEvaluationsService().get_annee(self.person)

    @cached_property
    def etudiant(self) -> 'Etudiant':
        return self.mes_programmes.etudiant

    @cached_property
    def formations(self) -> 'InscriptionFormation':
        return self.mes_programmes.formations

    @cached_property
    def mes_programmes(self) -> 'MesFormations':
        try:
            return MesProgrammesService().recuperer(self.person)
        except Http404:
            message = _("You are not registered for any course for the {annee_academique} academic year.").format(
                annee_academique=self.annee_academique
            )
            display_error_messages(
                self.request,
                messages_to_display=message
            )

    def dispatch(self, request, *args, **kwargs):
        if self.mes_programmes is None:
            return redirect(reverse("dashboard_home"))
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            'annee_academique': self.annee_academique,
            'etudiant': self.etudiant,
            'formations': self.formations,
            'mon_pae_et_mes_notes_url': reverse('performance_home'),
        }
