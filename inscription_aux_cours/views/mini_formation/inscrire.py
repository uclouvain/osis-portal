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
from django.urls import reverse
from django.utils.functional import cached_property
from django.views.generic import FormView
from osis_inscription_cours_sdk.model.liste_mini_formations import ListeMiniFormations
from osis_offer_enrollment_sdk.model.enrollment import Enrollment

from base.models import academic_year
from base.models.person import Person
from base.models.student import Student
from base.services.offer_enrollment import OfferEnrollmentService
from inscription_aux_cours.forms.mini_formation.formulaire_inscription import InscriptionMiniFormationForm
from inscription_aux_cours.services.mini_formation import MiniFormationService


class InscrireAuxMiniFormationsView(LoginRequiredMixin, FormView):
    name = 'inscrire-mini-formations'

    # TemplateView
    template_name = "inscription_aux_cours/mini_formation/inscrire.html"
    form_class = InscriptionMiniFormationForm

    @cached_property
    def person(self) -> 'Person':
        return Person.objects.get(user=self.request.user)

    @cached_property
    def student(self) -> 'Student':
        if self.formation:
            registration_id = self.formation.student_registration_id
            return Student.objects.get(registration_id=registration_id)

    # TODO should be returned by api
    @cached_property
    def annee_academique(self) -> 'int':
        return academic_year.starting_academic_year().year

    @property
    def sigle_formation(self) -> str:
        return self.kwargs['sigle_formation']

    @cached_property
    def formation(self) -> 'Enrollment':
        offer_enrollments = OfferEnrollmentService.get_my_enrollments_year_list(
            person=self.person, year=self.annee_academique
        )
        return next(
            (offer_enrollment for offer_enrollment in offer_enrollments
             if offer_enrollment.acronym == self.sigle_formation),
            None
        )

    @cached_property
    def mini_formations_inscriptibles(self) -> 'ListeMiniFormations':
        return MiniFormationService().get_mini_formations_inscriptibles(self.sigle_formation, self.person)

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            'student': self.student,
            'formation': self.formation,
            'annee_academique': self.annee_academique,
            'liste_mini_formations_inscriptibles': self.mini_formations_inscriptibles
        }

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()
        form_kwargs['liste_mini_formations'] = self.mini_formations_inscriptibles
        return form_kwargs

    def get_success_url(self):
        return reverse("inscription-aux-cours:selectionner-formation")
