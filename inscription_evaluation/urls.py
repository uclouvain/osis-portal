##############################################################################
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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
from django.urls import path, include

from inscription_evaluation.views.demande_inscription import EnregistrerDemandeInscriptionView
from inscription_evaluation.views.formulaire_inscription import FormulaireInscriptionView
from inscription_evaluation.views.recapitulatif import RecapitulatifView
from inscription_evaluation.views.selectionner_programme import SelectionnerProgrammeView
from inscription_evaluation.views.soumettre_demande_inscription import SoumettreDemandeInscriptionView

app_name = 'inscription-evaluation'
urlpatterns = [
    path('',SelectionnerProgrammeView.as_view(), name=SelectionnerProgrammeView.name),
    path(
        '<str:code_programme>/',
        include(
            [
                path('formulaire/', FormulaireInscriptionView.as_view(), name=FormulaireInscriptionView.name),
                path(
                    'enregistrer_proposition_inscriptions_evaluations/',
                    EnregistrerDemandeInscriptionView.as_view(),
                    name=EnregistrerDemandeInscriptionView.name,
                ),
                path('recapitulatif/', RecapitulatifView.as_view(), name=RecapitulatifView.name),
                path(
                    'soumettre_demande/',
                    SoumettreDemandeInscriptionView.as_view(),
                    name=SoumettreDemandeInscriptionView.name
                ),
            ]
        ),
    ),
]