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

from inscription_evaluation.services.formulaire_inscription import FormulaireInscriptionService
from inscription_evaluation.views.common import InscriptionEvaluationViewMixin


class FormulaireInscriptionView(LoginRequiredMixin, InscriptionEvaluationViewMixin, TemplateView):
    name = 'formulaire-inscription'

    # TemplateView
    template_name = "inscription_evaluation/formulaire_inscription.html"

    @cached_property
    def session_de_travail(self):
        # return self.formulaire.session_de_travail
        return {
            "annee": 2023,
            "numero_session": 3
        }

    @cached_property
    def etudiant(self):
#         return self.formulaire.etudiant
        return {
            "noma": "12345678",
            "nom": "Smith",
            "prenom": "Charles"
        }

    @cached_property
    def formation(self):
#         return self.formulaire.formation
        return {
            "code_programme": "LDROI100B",
            "sigle": "DROI1BA",
            "intitule": "Bachelier en droit"
        }

    @cached_property
    def contact_faculte(self):
#         return self.formulaire.contact_faculte
        return {
            "sigle_formation": "string",
            "pour_premiere_annee": True,
            "en_tete": "Secrétariat du 1er cycle ESPO",
            "email": "christine.vandiest@uclouvain.be"
        }

    @cached_property
    def inscriptions(self):
#         return self.formulaire.inscriptions
        return [
        {
            "unite_enseignement": {
                "code": "LDROI1001",
                "intitule": "Introduction au droit civil"
            },
            "credits_inscrits": "3.5",
            "etat_txt": "Hors progression",
            "peut_inscrire_evaluation": False,
            "type_inscription_possible": None,
            "type_inscription_possible_txt": None,
            "evaluation_session_1": {
                "type_inscription": "PREMIERE_INSCRIPTION",
                "type_inscription_txt": "Insc",
                "note": "15.0"
            },
            "evaluation_session_2": {
                "type_inscription": "PREMIERE_INSCRIPTION",
                "type_inscription_txt": "Insc",
                "note": "15.0"
            },
            "evaluation_session_3": {
                "type_inscription": "PREMIERE_INSCRIPTION",
                "type_inscription_txt": "Insc",
                "note": "15.0"
            },
            "note_finale": "15.0",
            "credite": "Oui"
        },
        {
            "unite_enseignement": {
                "code": "LDROI1002",
                "intitule": "Introduction au droit civil: partie 2"
            },
            "credits_inscrits": "5",
            "etat_txt": "Hors progression",
            "peut_inscrire_evaluation": False,
            "type_inscription_possible": None,
            "type_inscription_possible_txt": None,
            "evaluation_session_1": {
                "type_inscription": "INSCRIPTION_PARTIELLE",
                "type_inscription_txt": "Part",
                "note": "8.0"
            },
            "evaluation_session_2": {
                "type_inscription": "PREMIERE_INSCRIPTION",
                "type_inscription_txt": "Insc",
                "note": "9.0"
            },
            "evaluation_session_3": {
                "type_inscription": "REINSCRIPTION",
                "type_inscription_txt": "Reinsc",
                "note": ""
            },
            "note_finale": "",
            "credite": ""
        },
        {
            "unite_enseignement": {
                "code": "LDROI1003",
                "intitule": "Introduction au droit civil: partie 3"
            },
            "credits_inscrits": "5",
            "etat_txt": "",
            "peut_inscrire_evaluation": True,
            "type_inscription_possible": "PREMIERE_INSCRIPTION",
            "type_inscription_possible_txt": "Insc",
            "evaluation_session_1": {
                "type_inscription": "INSCRIPTION_PARTIELLE",
                "type_inscription_txt": "Part",
                "note": "8.0"
            },
            "evaluation_session_2": None,
            "evaluation_session_3": None,
            "note_finale": "",
            "credite": ""
        },
        {
            "unite_enseignement": {
                "code": "LDROI1004",
                "intitule": "Introduction au droit civil: partie 4"
            },
            "credits_inscrits": "5",
            "etat_txt": "",
            "peut_inscrire_evaluation": True,
            "type_inscription_possible": "PREMIERE_INSCRIPTION",
            "type_inscription_possible_txt": "Insc",
            "evaluation_session_1": {
                "type_inscription": "INSCRIPTION_PARTIELLE",
                "type_inscription_txt": "Part",
                "note": "8.0"
            },
            "evaluation_session_2": None,
            "evaluation_session_3": None,
            "note_finale": "",
            "credite": ""
        }
    ]

    @cached_property
    def peut_s_inscrire_a_minimum_une_evaluation(self):
        return any(inscription['peut_inscrire_evaluation'] for inscription in self.inscriptions)

    @cached_property
    def formulaire(self):
        # return FormulaireInscriptionService().recuperer(self.person, self.code_programme)
        return None

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            'session_de_travail': self.session_de_travail,
            'etudiant': self.etudiant,
            'formation': self.formation,
            'contact_faculte': self.contact_faculte,
            'inscriptions': self.inscriptions,
            'peut_s_inscrire_a_minimum_une_evaluation': self.peut_s_inscrire_a_minimum_une_evaluation,
        }
