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
from typing import Optional

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseNotFound, HttpResponseForbidden
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.functional import cached_property
from django.views.generic import FormView
from osis_inscription_cours_sdk.model.activites_aide_reussite import ActivitesAideReussite

from base.services.utils import ServiceException
from inscription_aux_cours.forms.activites_aide_reussite.activites import ActivitesAideReussiteForm
from inscription_aux_cours.services.activites_aide_reussite import ActivitesAideReussiteService
from inscription_aux_cours.views.common import InscriptionAuxCoursViewMixin


class FormulaireActivitesDeAideALaReussiteView(LoginRequiredMixin, InscriptionAuxCoursViewMixin, FormView):
    name = "formulaire-activites-aide-reussite"

    template_name = "inscription_aux_cours/activites_aide_reussite/formulaire.html"
    form_class = ActivitesAideReussiteForm

    @cached_property
    def activites_aide_reussite(self) -> Optional['ActivitesAideReussite']:
        return ActivitesAideReussiteService.get_activites_aide_reussite(self.person, self.code_programme)


    def get(self, request, *args, **kwargs):
        try:
            self.activites_aide_reussite
        except ServiceException as exc:
            if exc.status == HttpResponseForbidden.status_code:
                return redirect(
                    reverse("inscription-aux-cours:recapitulatif", kwargs={"code_programme": self.code_programme})
                )
            raise exc
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        if form.fields['completer_inscription_par_des_activites'].disabled:
            return super().form_valid(form)

        completer_inscription_par_des_activites = form.cleaned_data['completer_inscription_par_des_activites']
        try:
            if completer_inscription_par_des_activites:
                ActivitesAideReussiteService.demander_a_completer_inscription_par_des_activites_de_aide_a_la_reussite(
                    self.person,
                    self.code_programme
                )
            else:
                ActivitesAideReussiteService.\
                    demander_a_ne_pas_completer_inscription_par_des_activites_de_aide_a_la_reussite(
                    self.person,
                    self.code_programme
                )
        except ServiceException as service_exc:
            form.add_error("completer_inscription_par_des_activites", service_exc.messages)
            return self.form_invalid(form)

        return super().form_valid(form)


    def get_success_url(self):
        return reverse("inscription-aux-cours:recapitulatif", kwargs={"code_programme": self.code_programme})

    def get_initial(self):
        initial = super().get_initial()
        if self.activites_aide_reussite:
            initial['completer_inscription_par_des_activites'] = self.activites_aide_reussite.suivies_par_etudiant
        return initial

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()
        if self.activites_aide_reussite:
            form_kwargs['disabled'] = not self.activites_aide_reussite.demandees_par_etudiant
        return form_kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['activites_aide_reussite'] = self.activites_aide_reussite
        return context
