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

from inscription_evaluation.services.recapitulatif import RecapitulatifService
from inscription_evaluation.views.common import InscriptionEvaluationViewMixin


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
    def nombre_evaluation_organisee(self) -> int:
        # TODO: récupérer le nombre d'évaluation organisée pour cet.te étudiant.e
        # return self.recapitulatif.nombre_evaluation_organisee
        return 8

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            'session_de_travail': self.session_de_travail,
            'etudiant': self.etudiant,
            'contact_faculte': self.contact_faculte,
            'formation': self.formation,
            'inscriptions': self.inscriptions,
            'nombre_evaluation_organisee': self.nombre_evaluation_organisee,
        }
