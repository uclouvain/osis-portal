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
from django import forms
from osis_inscription_cours_sdk.model.liste_mini_formations import ListeMiniFormations


class InscriptionMiniFormationForm(forms.Form):
    mini_formations = forms.MultipleChoiceField(required=False)

    def __init__(self, *args, liste_mini_formations: 'ListeMiniFormations', **kwargs):
        super().__init__(*args, **kwargs)

        self.liste_mini_formations = liste_mini_formations
        self.__init_mini_formations_field()

    def __init_mini_formations_field(self):
        self.fields['mini_formations'].choices = [
            (mini_formation.code, mini_formation.code)
            for mini_formation in self.liste_mini_formations.mini_formations
        ]

