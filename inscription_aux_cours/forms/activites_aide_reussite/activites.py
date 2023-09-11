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
from django import forms
from django.utils.translation import gettext_lazy as _


class ActivitesAideReussiteForm(forms.Form):
    completer_inscription_par_des_activites = forms.NullBooleanField(
        required=True,
        label=_("I am supplementing my annual programme with learning support activities"),
        widget=forms.RadioSelect(
            choices=(
                (True, _('Yes')),
                (False, _('No'))
            )
        ),
    )

    def __init__(self, *args, disabled=False, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['completer_inscription_par_des_activites'].disabled = disabled
