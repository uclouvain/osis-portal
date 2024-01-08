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
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from django.shortcuts import redirect

from inscription_evaluation.services.recapitulatif import RecapitulatifService
from inscription_evaluation.views.common import InscriptionEvaluationViewMixin
from continuing_education.views.common import display_error_messages, display_success_messages
from inscription_evaluation.services.recapitulatif import RecapitulatifService
from base.services.utils import ServiceException


class RecapitulatifView(LoginRequiredMixin, InscriptionEvaluationViewMixin, TemplateView):
    name = "recapitulatif"

    template_name = "inscription_evaluation/recapitulatif.html"

    @cached_property
    def session_de_travail(self):
        # return self.recapitulatif.session_de_travail
        return {
            "annee": 2023,
            "numero_session": 3
        }

    @cached_property
    def etudiant(self):
        # return self.recapitulatif.etudiant
        return {
            "noma": "12345678",
            "nom": "Smith",
            "prenom": "Charles"
        }

    @cached_property
    def formation(self):
        # return self.recapitulatif.formation
        return {
            "code_programme": "LDROI100B",
            "sigle": "DROI1BA",
            "intitule": "Bachelier en droit"
        }

    @cached_property
    def contact_faculte(self):
        # return self.recapitulatif.contact_faculte
        return {
            "sigle_formation": "string",
            "pour_premiere_annee": True,
            "en_tete": "Secrétariat du 1er cycle ESPO",
            "email": "christine.vandiest@uclouvain.be"
        }

    @cached_property
    def inscriptions(self):
        # return self.recapitulatif.inscriptions
        return [
            {
              "unite_enseignement": {
                "code": "LDROI1001",
                "intitule": "Introduction au droit civil"
              },
              "type_inscription": "PREMIERE_INSCRIPTION",
              "type_inscription_txt": "Insc"
            }
        ]

    @cached_property
    def recapitulatif(self):
        # return RecapitulatifService.recuperer(self.person, self.code_programme)
        return None

    @cached_property
    def total_evaluations_organisees(self) -> int:
        # return self.recapitulatif.total_evaluations_organisees
        return 8

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            'session_de_travail': self.session_de_travail,
            'etudiant': self.etudiant,
            'contact_faculte': self.contact_faculte,
            'formation': self.formation,
            'inscriptions': self.inscriptions,
            'total_evaluations_organisees': self.total_evaluations_organisees,
        }

    def post(self, request, *args, **kwargs):
        try:
            # self.soumettre_demande()
            display_success_messages(
                request,
                self.get_success_message(),
            )
        except ServiceException as e:
            display_error_messages(request, e.messages)
        return redirect('inscription-evaluation:selectionner-programme')

    def get_success_message(self):
        return _(
            "Evaluation registration form for %(sigle_formation)s has been successfully submitted. "
            "A confirmation email will be sent to %(email)s."
        ) % {'email': self.request.user.person.email, 'sigle_formation': self.formation.get('sigle')}

    def soumettre_demande(self):
        RecapitulatifService().soumettre(
            self.person,
            code_programme=self.code_programme,
        )
