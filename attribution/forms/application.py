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


class ApplicationForm(forms.Form):

    charge_lecturing = forms.DecimalField(max_digits=5, decimal_places=2, initial=0, localize=True, required=False)
    charge_practical = forms.DecimalField(max_digits=5, decimal_places=2, initial=0, localize=True, required=False)
    course_summary = forms.Textarea()
    remark = forms.Textarea() #250

    def __init__(self, *args, **kwargs):
        super(ApplicationForm, self).__init__(*args, **kwargs)
        self._initial_data = self.__dict__.copy()


    def clean(self):
        cleaned_data = super(ApplicationForm, self).clean()
        charge_lecturing = cleaned_data.get("charge_lecturing")
        if charge_lecturing and charge_lecturing < 0:
            self.errors['charge_lecturing'] = _('not_positive')
        charge_practical = cleaned_data.get("charge_practical")
        if charge_practical and charge_practical < 0:
            self.errors['charge_practical'] = _('not_positive')
        return cleaned_data


    def clean_charge_lecturing(self):
        return self.validate_charge('charge_lecturing')

    def validate_charge(self, field_name):
        if not self[field_name].html_name in self.data or \
                        self.cleaned_data.get(field_name) is None:
            return self.fields[field_name].initial
        return self.cleaned_data.get(field_name)

    def clean_charge_practical(self):
        return self.validate_charge('charge_practical')