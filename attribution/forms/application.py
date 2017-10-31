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

from attribution.business import tutor_application
from base.forms.base_forms import BootstrapForm

MAXIMUM_REMARK_LENGTH = 250


class ApplicationForm(forms.Form):
    charge_lecturing = forms.DecimalField(max_digits=5, decimal_places=2, initial=0, required=False, localize=True)
    charge_practical = forms.DecimalField(max_digits=5, decimal_places=2, initial=0, required=False, localize=True)
    course_summary = forms.CharField(widget=forms.Textarea, required=False)
    remark = forms.CharField(widget=forms.Textarea, required=False)

    acronym = forms.CharField(widget=forms.HiddenInput, required=False)
    year = forms.IntegerField(widget=forms.HiddenInput, required=False)

    def __init__(self, *args, **kwargs):
        self.learning_container_year = kwargs.pop('learning_container_year')
        self.global_id = kwargs.pop('global_id')
        self._load_vacant_attribution()
        super(ApplicationForm, self).__init__(*args, **kwargs)

    def _load_vacant_attribution(self):
        self.attribution_vacant = tutor_application.get_attribution_vacant(
            global_id=self.global_id,
            learning_container_year=self.learning_container_year
        )

    def clean_acronym(self):
        return self.learning_container_year.acronym

    def clean_year(self):
        return self.learning_container_year.academic_year.year

    def clean_charge_lecturing(self):
        data_cleaned = self.cleaned_data['charge_lecturing']
        if data_cleaned is not None:
            return str(data_cleaned)
        return data_cleaned

    def clean_charge_practical(self):
        data_cleaned = self.cleaned_data['charge_practical']
        if data_cleaned is not None:
            return str(data_cleaned)
        return data_cleaned

    # max_charge_lecturing = forms.DecimalField(widget=forms.HiddenInput, max_digits=5, decimal_places=2, disabled=True)
    # max_charge_practical = forms.DecimalField(widget=forms.HiddenInput, max_digits=5, decimal_places=2, disabled=True)

    # def value_if_empty(self, field_name):
    #     if not self[field_name].html_name in self.data or \
    #                     self.cleaned_data.get(field_name) is None:
    #         return self.fields[field_name].initial
    #
    #     return self.cleaned_data.get(field_name)

    # def clean(self):
    #     cleaned_data = super(ApplicationForm, self).clean()
    #     charge_lecturing = cleaned_data.get("charge_lecturing")
    #     if charge_lecturing:
    #         if charge_lecturing < 0:
    #             self.errors['charge_lecturing'] = _('not_positive')
    #         else:
    #             max_charge_lecturing = cleaned_data.get("max_charge_lecturing")
    #             if charge_lecturing > max_charge_lecturing:
    #                 self.errors['charge_lecturing'] = "{0} (max: {1})".format(_('too_much'),max_charge_lecturing)
    #
    #     charge_practical = cleaned_data.get("charge_practical")
    #     if charge_practical:
    #         if charge_practical < 0:
    #             self.errors['charge_practical'] = _('not_positive')
    #         else:
    #             max_charge_practical = cleaned_data.get("max_charge_practical")
    #
    #             if charge_practical > max_charge_practical:
    #                 self.errors['charge_practical'] = "{0} (max: {1})".format(_('too_much'),max_charge_practical)
    #     remark = cleaned_data.get("remark")
    #     if remark and len(remark) > MAXIMUM_REMARK_LENGTH:
    #         self.errors['remark'] = _('250_characters_max')
    #
    #     return cleaned_data
    #
    # def clean_charge_lecturing(self):
    #     return self.value_if_empty('charge_lecturing')
    #
    # def clean_charge_practical(self):
    #     return self.value_if_empty('charge_practical')


class VacantAttributionFilterForm(BootstrapForm):
    learning_container_acronym = forms.CharField(required=True, max_length=15)

    def clean_learning_container_acronym(self):
        data_cleaned = self.cleaned_data['learning_container_acronym']
        if isinstance(data_cleaned, str):
            return data_cleaned.upper()
        return data_cleaned
