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
from django.urls import path, include, re_path

from inscription_aux_cours.views.activites_aide_reussite.formulaire import FormulaireActivitesDeAideALaReussiteView
from inscription_aux_cours.views.cours.formulaire import FormulaireCompositionPAEView
from inscription_aux_cours.views.cours.ma_proposition_de_pae import MaPropositionDePaeView
from inscription_aux_cours.views.cours.mon_pae_valide_jury import MonPaeValideJuryView
from inscription_aux_cours.views.cours.proposition_programme_annuel import EnregistrerPropositionProgrammeAnnuelView
from inscription_aux_cours.views.cours.recapitulatif import RecapitulatifView
from inscription_aux_cours.views.cours.soumettre_proposition import SoumettrePropositionView
from inscription_aux_cours.views.inscription_non_autorisee import InscriptionNonAutoriseeView
from inscription_aux_cours.views.mini_formation.desinscrire import DesinscrireAUneMiniFormationView
from inscription_aux_cours.views.mini_formation.formulaire import FormulaireMiniFormationsView
from inscription_aux_cours.views.mini_formation.inscrire import InscrireAUneMiniFormationView
from inscription_aux_cours.views.mini_formation.recapitulatif import RecapitulatifInscriptionsMiniFormationsView
from inscription_aux_cours.views.progression.barre_de_progression_de_bloc_1 import BarreDeProgressionDeBloc1View
from inscription_aux_cours.views.progression.barre_de_progression_de_complement import (
    BarreDeProgressionDeComplementView,
)
from inscription_aux_cours.views.progression.barre_de_progression_de_cycle import BarreDeProgressionDeCycleView
from inscription_aux_cours.views.selectionner_formation import SelectionnerFormationView

app_name = 'inscription-aux-cours'
urlpatterns = [
    path('', SelectionnerFormationView.as_view(), name=SelectionnerFormationView.name),
    path(
        '<str:code_programme>/',
        include(
            [
                path('non_autorisee/', InscriptionNonAutoriseeView.as_view(), name=InscriptionNonAutoriseeView.name),
                path(
                    'formulaire/',
                    FormulaireCompositionPAEView.as_view(),
                    name=FormulaireCompositionPAEView.name,
                ),
                path('recapitulatif/', RecapitulatifView.as_view(), name=RecapitulatifView.name),
                path(
                    'enregistrer_proposition_programme_annuel/',
                    EnregistrerPropositionProgrammeAnnuelView.as_view(),
                    name=EnregistrerPropositionProgrammeAnnuelView.name,
                ),
                path('soumettre_proposition/', SoumettrePropositionView.as_view(), name=SoumettrePropositionView.name),
                path('ma_proposition_de_pae/', MaPropositionDePaeView.as_view(), name=MaPropositionDePaeView.name),
                path('mon_pae_valide_jury/', MonPaeValideJuryView.as_view(), name=MonPaeValideJuryView.name),
                path(
                    'mineures_options/',
                    include(
                        [
                            path(
                                'recapitulatif/',
                                RecapitulatifInscriptionsMiniFormationsView.as_view(),
                                name=RecapitulatifInscriptionsMiniFormationsView.name,
                            ),
                            path(
                                'formulaire/',
                                FormulaireMiniFormationsView.as_view(),
                                name=FormulaireMiniFormationsView.name,
                            ),
                            path(
                                'inscrire/',
                                InscrireAUneMiniFormationView.as_view(),
                                name=InscrireAUneMiniFormationView.name,
                            ),
                            path(
                                'desinscrire/',
                                DesinscrireAUneMiniFormationView.as_view(),
                                name=DesinscrireAUneMiniFormationView.name,
                            ),
                        ]
                    ),
                ),
                path(
                    'activites_aide_reussite/',
                    FormulaireActivitesDeAideALaReussiteView.as_view(),
                    name=FormulaireActivitesDeAideALaReussiteView.name,
                ),
            ]
        ),
    ),
    re_path(
        r'^(?P<sigle_programme>[\w ]+([/ ]\w{1,2})?)/',
        include(
            [
                path(
                    'barre_de_progression_de_cycle/',
                    BarreDeProgressionDeCycleView.as_view(),
                    name=BarreDeProgressionDeCycleView.name,
                ),
                path(
                    'barre_de_progression_de_complement/',
                    BarreDeProgressionDeComplementView.as_view(),
                    name=BarreDeProgressionDeComplementView.name,
                ),
                path(
                    'barre_de_progression_de_bloc_1/',
                    BarreDeProgressionDeBloc1View.as_view(),
                    name=BarreDeProgressionDeBloc1View.name,
                ),
            ]
        ),
    ),
]
