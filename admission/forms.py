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


class NewAccountForm(forms.Form):
    first_name_new = forms.CharField(required=True, max_length=30)
    last_name_new = forms.CharField(required=True, max_length=30)
    email_new = forms.EmailField(help_text='Merci d\'encoder une adresse email correcte.', required=True)
    email_new_confirm = forms.EmailField(help_text='Merci d\'encoder une adresse email correcte.', required=True)
    password_new = forms.CharField(widget=forms.PasswordInput, required=True)
    password_new_confirm = forms.CharField(widget=forms.PasswordInput, required=True)
    verification = forms.CharField(required=True)

    def __init__(self, *args, **kwargs):
        super(NewAccountForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super(NewAccountForm, self).clean()
        email_new = cleaned_data.get("email_new")
        email_new_confirm = cleaned_data.get("email_new_confirm")
        if email_new != email_new_confirm:
            self.errors['email_new_confirm'] = "Les 2 emails sont différents"
        password_new = cleaned_data.get("password_new")
        password_new_confirm = cleaned_data.get("password_new_confirm")
        if password_new != password_new_confirm:
            self.errors['password_new_confirm'] = "Les 2 mots de passe sont différents"
        if password_new is not None and len(password_new) < 8:
            self.errors['password_new'] = "This password is too short. It must contain at least 8 characters."
        return cleaned_data

    def clean_password_new(self):
        data = self.cleaned_data['password_new']
        return data.strip()

    def clean_password_new_confirm(self):
        data = self.cleaned_data['password_new_confirm']
        return data.strip()


class AccountForm(forms.Form):
    email =    forms.EmailField(help_text='Merci d\'encoder une adresse email correcte.', required = True)
    password = forms.CharField(widget=forms.PasswordInput, required = True)

    def __init__(self, *args, **kwargs):
        super(AccountForm, self).__init__(*args, **kwargs)

    def clean_password(self):
        data = self.cleaned_data['password']
        return data.strip()


class NewPasswordForm(forms.Form):
    password_new =         forms.CharField(widget=forms.PasswordInput, required = True)
    password_new_confirm = forms.CharField(widget=forms.PasswordInput, required = True)

    def __init__(self, *args, **kwargs):
        super(NewPasswordForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super(NewPasswordForm, self).clean()
        password_new = cleaned_data.get("password_new")
        password_new_confirm = cleaned_data.get("password_new_confirm")
        if password_new != password_new_confirm:
            self.errors['password_new_confirm'] = "Les 2 mots de passe sont différents"
        if password_new is not None and len(password_new) < 8:
            self.errors['password_new'] = "This password is too short. It must contain at least 8 characters."
        return cleaned_data

    def clean_password_new(self):
        data = self.cleaned_data['password_new']
        return data.strip()

    def clean_password_new_confirm(self):
        data = self.cleaned_data['password_new_confirm']
        return data.strip()


class PersonForm(forms.Form):

    last_name               = forms.CharField(help_text='Champ obligatoire.', required=True)
    first_name              = forms.CharField(help_text='Champ obligatoire.', required=True)
    birth_date              = forms.DateField(help_text='Champ obligatoire.',
                                              required=True,input_formats=['%d/%m/%Y'],
                                              widget=forms.DateInput(format = '%d/%m/%Y'))
    birth_place             = forms.CharField(help_text='Champ obligatoire.', required=True)
    birth_country           = forms.CharField(help_text='Champ obligatoire.', required=True)
    gender                  = forms.CharField(help_text='Champ obligatoire.', required=True)
    civil_status            = forms.CharField(help_text='Champ obligatoire.', required=True)
    nationality             = forms.CharField(help_text='Champ obligatoire.', required=True)
    legal_adr_street        = forms.CharField(help_text='Champ obligatoire.', required=True)
    legal_adr_number        = forms.CharField(help_text='Champ obligatoire.', required=True)
    legal_adr_postal_code   = forms.CharField(help_text='Champ obligatoire.', required=True)
    legal_adr_city          = forms.CharField(help_text='Champ obligatoire.', required=True)
    legal_adr_country       = forms.CharField(help_text='Champ obligatoire.', required=True)
    same_contact_legal_addr = forms.CharField(help_text='Champ obligatoire.', required=True)
    contact_adr_postal_code = forms.CharField(help_text='Champ obligatoire.', required=False)
    contact_adr_city        = forms.CharField(help_text='Champ obligatoire.', required=False)
    contact_adr_country     = forms.CharField(help_text='Champ obligatoire.', required=False)
    additional_email        = forms.EmailField(help_text='Merci d\'encoder une adresse email correcte.', required=True)
    ucl_last_year           = forms.IntegerField(required=False)


    def __init__(self, *args, **kwargs):
        super(PersonForm, self).__init__(*args, **kwargs)

    def clean(self):
        print('clean')
        cleaned_data = super(PersonForm, self).clean()



        same_contact_legal_addr = cleaned_data.get("same_contact_legal_addr")

        if same_contact_legal_addr == "false":
            contact_adr_postal_code  = cleaned_data.get("contact_adr_postal_code")
            if contact_adr_postal_code is None or len(contact_adr_postal_code) <= 0:
                self.errors['contact_adr_postal_code'] = "Champ obligatoire"

            contact_adr_city = cleaned_data.get("contact_adr_city")
            print(contact_adr_city)
            if contact_adr_city is None or len(contact_adr_city) <= 0:
                self.errors['contact_adr_city'] = "Champ obligatoire"

            contact_adr_country  = cleaned_data.get("contact_adr_country")
            if contact_adr_country is None or len(contact_adr_country) <= 0:
                self.errors['contact_adr_country'] = "Champ obligatoire"

        previous_enrollment = cleaned_data.get("previous_enrollment")

        if previous_enrollment:
            register_number = cleaned_data.get("register_number")
            if register_number is not None and len(register_number) <= 0:
                self.errors['register_number'] = "Champ obligatoire"
            ucl_last_year = cleaned_data.get("ucl_last_year")
            if ucl_last_year is not None and len(ucl_last_year) <= 0:
                self.errors['ucl_last_year'] = "Champ obligatoire"

        return cleaned_data
