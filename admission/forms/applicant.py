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
from admission.validators import date_validator


class ApplicantForm(forms.Form):
    REQUIRED_ARGUMENTS = dict(required=True, error_messages=dict(required=_('mandatory_field')))

    GENDER_CHOICES = (
        ('MALE', 'MALE'),
        ('FEMALE', 'FEMALE')
    )

    last_name = forms.CharField(**REQUIRED_ARGUMENTS)
    first_name = forms.CharField(**REQUIRED_ARGUMENTS)
    birth_date = forms.DateField(input_formats=['%d/%m/%Y'],
                                 widget=forms.DateInput(format='%d/%m/%Y'),
                                 validators=[date_validator.validate_birth_date],
                                 required=True,
                                 error_messages={
                                     'required': _('mandatory_field'),
                                     'invalid': _('invalid_date')
                                 })
    birth_place = forms.CharField(**REQUIRED_ARGUMENTS)
    birth_country = forms.CharField(**REQUIRED_ARGUMENTS)
    gender = forms.ChoiceField(choices=GENDER_CHOICES, **REQUIRED_ARGUMENTS)
    civil_status = forms.CharField(**REQUIRED_ARGUMENTS)
    number_children = forms.IntegerField(validators=[MinValueValidator(0)], required=False)
    nationality = forms.CharField(**REQUIRED_ARGUMENTS)
    legal_adr_street = forms.CharField(**REQUIRED_ARGUMENTS)
    legal_adr_number = forms.CharField(**REQUIRED_ARGUMENTS)
    legal_adr_postal_code = forms.CharField(**REQUIRED_ARGUMENTS)
    legal_adr_city = forms.CharField(**REQUIRED_ARGUMENTS)
    legal_adr_country = forms.CharField(**REQUIRED_ARGUMENTS)
    same_contact_legal_addr = forms.CharField(**REQUIRED_ARGUMENTS)
    contact_adr_street = forms.CharField(required=False)
    contact_adr_number = forms.CharField(required=False)
    contact_adr_postal_code = forms.CharField(required=False)
    contact_adr_city = forms.CharField(required=False)
    contact_adr_country = forms.CharField(required=False)
    previous_enrollment = forms.CharField(required=False)
    registration_id = forms.CharField(required=False)
    last_academic_year = forms.IntegerField(required=False)
    national_id = forms.CharField(required=False)
    id_card_number = forms.CharField(required=False)
    passport_number = forms.CharField(required=False)

    def __init__(self, *args, **kwargs):
        super(ApplicantForm, self).__init__(*args, **kwargs)
        self._initial_data = dict(self.__dict__)

    def clean(self):
        cleaned_data = super(ApplicantForm, self).clean()
        same_contact_legal_addr = cleaned_data.get("same_contact_legal_addr")

        if same_contact_legal_addr == "false":
            contact_adr_street = cleaned_data.get("contact_adr_street")
            if contact_adr_street is None or len(contact_adr_street) <= 0:
                self.errors['contact_adr_street'] = _('mandatory_field')

            contact_adr_number = cleaned_data.get("contact_adr_number")
            if contact_adr_number is None or len(contact_adr_number) <= 0:
                self.errors['contact_adr_number'] = _('mandatory_field')

            contact_adr_postal_code = cleaned_data.get("contact_adr_postal_code")
            if contact_adr_postal_code is None or len(contact_adr_postal_code) <= 0:
                self.errors['contact_adr_postal_code'] = _('mandatory_field')

            contact_adr_city = cleaned_data.get("contact_adr_city")

            if contact_adr_city is None or len(contact_adr_city) <= 0:
                self.errors['contact_adr_city'] = _('mandatory_field')

            contact_adr_country = cleaned_data.get("contact_adr_country")
            if contact_adr_country is None or len(contact_adr_country) <= 0:
                self.errors['contact_adr_country'] = _('mandatory_field')

        previous_enrollment = cleaned_data.get("previous_enrollment")

        if previous_enrollment == 'true':
            registration_id = cleaned_data.get("registration_id")

            if registration_id is None or len(registration_id) <= 0:
                self.errors['registration_id'] = _('mandatory_field')

            last_academic_year = cleaned_data.get("last_academic_year")

            if last_academic_year is None or last_academic_year <= 0:
                self.errors['last_academic_year'] = _('numeric_field')

        nationality = cleaned_data.get("nationality")
        if nationality == '-1':
            self.errors['nationality'] = _('mandatory_field')

        birth_country = cleaned_data.get("birth_country")
        if birth_country == '-1':
            self.errors['birth_country'] = _('mandatory_field')

        national_id = cleaned_data.get("national_id")
        id_card_number = cleaned_data.get("id_card_number")
        passport_number = cleaned_data.get("passport_number")

        if national_id == '' and id_card_number =='' and passport_number == '' :
            self.errors['passport_number'] = _('no_identification_number')
        return cleaned_data
