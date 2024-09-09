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
import datetime
from decimal import Decimal

from django import forms
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _, pgettext

from base.forms.base_forms import BootstrapForm
from base.models.entity_version import search

MAXIMUM_REMARK_LENGTH = 250


class ApplicationForm(BootstrapForm):
    code = forms.CharField(disabled=True, required=False)
    title = forms.CharField(disabled=True, required=False)
    charge_lecturing_asked = forms.DecimalField(
        max_digits=6,
        decimal_places=2,
        initial=Decimal('0.0'),
        required=False,
        localize=True,
        validators=[MinValueValidator(0)]
    )
    charge_practical_asked = forms.DecimalField(
        max_digits=6,
        decimal_places=2,
        initial=Decimal('0.0'),
        required=False,
        localize=True,
        validators=[MinValueValidator(0)],
    )
    course_summary = forms.CharField(widget=forms.Textarea(attrs={'rows': 4}), required=False)
    remark = forms.CharField(widget=forms.Textarea(attrs={'rows': 4}), required=False, max_length=MAXIMUM_REMARK_LENGTH)

    def __init__(self, *args, vacant_course=None, **kwargs):
        self.vacant_course = vacant_course
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super(ApplicationForm, self).clean()

        if cleaned_data.get('charge_lecturing_asked') is None and cleaned_data.get('charge_practical_asked') is None:
            raise forms.ValidationError(_('Lecturing charge or practical charge must be filled'))

    def clean_charge_lecturing_asked(self):
        data_cleaned = self.cleaned_data['charge_lecturing_asked']
        if data_cleaned is not None:
            max_value = getattr(self.vacant_course, 'lecturing_volume_available', '0.0')
            if data_cleaned > Decimal(max_value):
                self.add_error('charge_lecturing_asked', "{0} (max: {1})".format(_('Too much'), max_value))
            return Decimal('{:.2f}'.format(data_cleaned))
        return Decimal('0.0')

    def clean_charge_practical_asked(self):
        data_cleaned = self.cleaned_data['charge_practical_asked']
        if data_cleaned is not None:
            max_value = getattr(self.vacant_course, 'practical_volume_available', '0.0')
            if data_cleaned > Decimal(max_value):
                self.add_error('charge_practical_asked', "{0} (max: {1})".format(_('Too much'), max_value))
            return Decimal('{:.2f}'.format(data_cleaned))
        return Decimal('0.0')

    def clean_course_summary(self):
        return self.cleaned_data['course_summary'] or ''

    def clean_remark(self):
        return self.cleaned_data['remark'] or ''


class VacantAttributionFilterForm(BootstrapForm):
    faculty = forms.ModelChoiceField(
        queryset=search(entity_type="FACULTY", date=datetime.date.today()),
        widget=forms.Select(attrs={'class':'form-select'}),
        empty_label=pgettext("plural", "All"),
        required=False,
    )

    learning_container_acronym = forms.CharField(required=False, max_length=15,
                                                 widget=forms.TextInput(attrs={'autofocus': 'autofocus'}))

    def clean_learning_container_acronym(self):
        data_cleaned = self.cleaned_data['learning_container_acronym']
        if isinstance(data_cleaned, str):
            return data_cleaned.upper()
        return data_cleaned

    def is_valid(self):
        return super(VacantAttributionFilterForm, self).is_valid() and self._has_mininum_criteria()

    def _has_mininum_criteria(self):
        cleaned_data = super(VacantAttributionFilterForm, self).clean()
        if cleaned_data['faculty'] is None and \
                (
                        cleaned_data['learning_container_acronym'] is None
                        or len(cleaned_data['learning_container_acronym']) == 0
                ):
            self._errors['learning_container_acronym'] = _(
                'Please precise at least a faculty or a code (or a part of a code)')
            return False
        return True
