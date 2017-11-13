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
from django.core.validators import MinValueValidator
from django.utils.translation import ugettext_lazy as _

from attribution.business import attribution
from base.forms.base_forms import BootstrapForm
from base.models.enums import learning_component_year_type

MAXIMUM_REMARK_LENGTH = 250


class ApplicationForm(BootstrapForm):
    charge_lecturing_asked = forms.DecimalField(max_digits=5, decimal_places=1, initial=0, required=False, localize=True,
                                          validators=[MinValueValidator(0)])
    charge_practical_asked = forms.DecimalField(max_digits=5, decimal_places=1, initial=0, required=False, localize=True,
                                          validators=[MinValueValidator(0)])
    course_summary = forms.CharField(widget=forms.Textarea(attrs={'rows': 4}), required=False)
    remark = forms.CharField(widget=forms.Textarea(attrs={'rows': 4}), required=False, max_length=MAXIMUM_REMARK_LENGTH)

    acronym = forms.CharField(widget=forms.HiddenInput, required=False)
    year = forms.IntegerField(widget=forms.HiddenInput, required=False)

    def __init__(self, *args, **kwargs):
        self.learning_container_year = kwargs.pop('learning_container_year')
        self._load_vacant_attribution()
        super(ApplicationForm, self).__init__(*args, **kwargs)

    def _load_vacant_attribution(self):
        self.attribution_vacant = attribution.get_attribution_vacant(
            learning_container_year=self.learning_container_year
        )

    def clean(self):
        cleaned_data = super(ApplicationForm, self).clean()

        if not cleaned_data.get('charge_lecturing_asked') and not cleaned_data.get('charge_practical_asked'):
            raise forms.ValidationError(_('charge_lecturing_asked_or_charge_practical_asked_must_be_filled'))

    def clean_acronym(self):
        return self.learning_container_year.acronym

    def clean_year(self):
        return self.learning_container_year.academic_year.year

    def clean_charge_lecturing_asked(self):
        data_cleaned = self.cleaned_data['charge_lecturing_asked']
        if data_cleaned is not None:
            max_value = self.attribution_vacant.get(learning_component_year_type.LECTURING, 0)
            if data_cleaned > max_value:
                self.add_error('charge_lecturing_asked', "{0} (max: {1})".format(_('too_much'),max_value))
            return data_cleaned
        return data_cleaned

    def clean_charge_practical_asked(self):
        data_cleaned = self.cleaned_data['charge_practical_asked']
        if data_cleaned is not None:
            max_value = self.attribution_vacant.get(learning_component_year_type.PRACTICAL_EXERCISES, 0)
            if data_cleaned > max_value:
                self.add_error('charge_practical_asked', "{0} (max: {1})".format(_('too_much'),max_value))
            return data_cleaned
        return data_cleaned


class VacantAttributionFilterForm(BootstrapForm):
    learning_container_acronym = forms.CharField(required=True, max_length=15)

    def clean_learning_container_acronym(self):
        data_cleaned = self.cleaned_data['learning_container_acronym']
        if isinstance(data_cleaned, str):
            return data_cleaned.upper()
        return data_cleaned
