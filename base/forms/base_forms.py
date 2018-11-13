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
from django.utils.translation import ugettext_lazy as _
from base.models import student as std_model
from base.models import tutor as tutor_model


class RegistrationIdForm(forms.Form):
    registration_id = forms.CharField()

    def clean(self):
        cleaned_data = super(RegistrationIdForm, self).clean()
        registration_id = cleaned_data.get('registration_id')
        if registration_id:
            student = std_model.find_by_registration_id(registration_id)
            if student is None:
                self.add_error('registration_id', _('no student with this registration_id'))


class GlobalIdForm(forms.Form):
    global_id = forms.CharField()

    def clean(self):
        cleaned_data = super(GlobalIdForm, self).clean()
        global_id = cleaned_data.get('global_id')
        if global_id:
            tutor = tutor_model.find_by_person_global_id(global_id)
            if tutor is None:
                self.add_error('global_id', _('no tutor with this global_id'))


class BootstrapModelForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(BootstrapModelForm, self).__init__(*args, **kwargs)
        set_form_control(self)


class BootstrapForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super(BootstrapForm, self).__init__(*args, **kwargs)
        set_form_control(self)


def set_form_control(self):
    for field in self.fields:
        attr_class = self.fields[field].widget.attrs.get('class') or ''
        self.fields[field].widget.attrs['class'] = attr_class + ' form-control'
