##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2016 Université catholique de Louvain (http://www.uclouvain.be)
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

from django import forms
from django.forms import ModelForm
from dissertation.models.dissertation import Dissertation
from dissertation.models.dissertation_update import DissertationUpdate
from dissertation.models.dissertation_role import DissertationRole


class DissertationForm(ModelForm):
    class Meta:
        model = Dissertation
        fields = ('title', 'author', 'offer_year_start', 'proposition_dissertation', 'description', 'defend_year',
                  'defend_periode')
        widgets = {'author': forms.HiddenInput()}


class DissertationRoleForm(ModelForm):
    class Meta:
        model = DissertationRole
        fields = ('dissertation', 'status', 'adviser')
        widgets = {'dissertation': forms.HiddenInput(),
                   'status': forms.HiddenInput()}


class DissertationTitleForm(ModelForm):
    class Meta:
        model = Dissertation
        fields = ('title',)


class DissertationUpdateForm(ModelForm):
    class Meta:
        model = DissertationUpdate
        fields = ('justification',)
