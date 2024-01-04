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
from django.utils.functional import cached_property
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin

from base.models.person import Person
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
    def etudiant(self):
        # return self.mes_programmes.etudiant
        return {
            "noma": "12345678",
            "nom": "Smith",
            "prenom": "Charles",
        }

    @cached_property
    def formations(self):
        # return self.mes_programmes.formations
        return [
            {
                "code_programme": "LDROI100B",
                "sigle": "DROI1BA",
                "intitule": "Bachelier en droit",
                "periode_inscription": {
                    "annee": 2023,
                    "numero_session": 3,
                    "date_ouverture": "2023-12-11",
                    "date_fermeture": "2023-12-11",
                },
                "peut_inscrire_aux_evaluations": False,
                "raisons_peut_pas_inscrire": [
                    "L'inscription aux évaluations en ligne n'est pas ouverte pour cette formation."
                ],
                "contact_faculte":{
                    "sigle_formation": "string",
                    "pour_premiere_annee": True,
                    "en_tete": "Secrétariat du 1er cycle ESPO",
                    "email": "christine.vandiest@uclouvain.be"
                }
            },
            {
                "code_programme": "LECGE100B",
                "sigle": "ECGE1BA",
                "intitule": "Bachelier en sciences économiques et de gestion",
                "periode_inscription": {
                    "annee": 2023,
                    "numero_session": 3,
                    "date_ouverture": "2023-12-11",
                    "date_fermeture": "2023-12-11",
                },
                "peut_inscrire_aux_evaluations": True,
                "raisons_peut_pas_inscrire": [
                ],
                "contact_faculte":{
                    "sigle_formation": "string",
                    "pour_premiere_annee": True,
                    "en_tete": "Secrétariat du 1er cycle ESPO",
                    "email": "christine.vandiest@uclouvain.be"
                }
            }
        ]

    @cached_property
    def mes_programmes(self):
        # return MesProgrammesService().recuperer(self.person)
        return None

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            'annee_academique': self.annee_academique,
            'etudiant': self.etudiant,
            'formations': self.formations,
        }