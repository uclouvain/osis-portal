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
from typing import List, Tuple

from dal import autocomplete
from django import forms
from django.utils.translation import gettext_lazy as _


class InscriptionHorsProgrammeForm(forms.Form):
    annee = forms.IntegerField(disabled=True, widget=forms.HiddenInput)
    code_mini_formation = forms.ChoiceField()
    cours = forms.MultipleChoiceField(
        required=False,
        label=_('Learning Unit Year').capitalize(),
        widget=autocomplete.Select2Multiple(
            url='learning-unit:learning_unit_year_autocomplete',
            attrs={
                'data-html': True,
                'data-minimum-input-length': 2,
                'data-placeholder': _('Search by code (example: LCHIM1111)')
            },
            forward=["annee"]
        )
    )

    def __init__(self, choix_mini_formation: List[Tuple], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._init_contexte(choix_mini_formation)

    def _init_contexte(self, contextes: List[Tuple]):
        self.fields['code_mini_formation'].choices = contextes
        if len(contextes) == 1:
            self.fields['code_mini_formation'].required = False
