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
from django.utils.translation import ugettext_lazy as _

from admission.models.person import Person #AA
from admission.models.personAddress import PersonAddress #AA

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


#HOW TO EXTRACT FamilyName and FirstName from User ?

class PersonForm(forms.ModelForm):

    LASTREGISTRATION_CHOICES = (
        ('1', _('Oui')),
        ('2', _('Non')))

    lastregistration_choice = forms.ChoiceField(widget=forms.RadioSelect, choices=LASTREGISTRATION_CHOICES, initial='1')

    def __init__(self, *args, **kwargs):
        super(PersonForm, self).__init__(*args, **kwargs)
        self.fields['user'].help_text = "(ex:  Van der Elst /...)"
        self.fields['middle_name'].help_text = "(ex:  Pierre, Paul, Jacques)"
        self.fields['birth_date'].help_text = "(jj/mm/aaaa)"
        self.fields['birth_place'].help_text = "(ex:  Louvain-la-Neuve ...)"

        self.fields['user'].label = "Nom"
        self.fields['middle_name'].label="Autres prénoms"
        self.fields['birth_date'].label="Date de naissance *"
        self.fields['birth_place'].label="Lieu de naissance *"
        self.fields['birth_country'].label="Pays de naissance *"
        self.fields['gender'].label="Genre *"
        self.fields['civil_status'].label="Etat civil *"
        self.fields['number_children'].label="Nombre d\'enfants"
        self.fields['spouse_name'].label="Nom conjoint"
        self.fields['nationality'].label="Nationalité *"
        self.fields['national_id'].label="Numéro du registre national"
        self.fields['id_card_number'].label="Numéro de carte d\'identité"
        self.fields['passport_number'].label="Numéro de passport"
        self.fields['phone_mobile'].label="GSM"
        self.fields['phone'].label="Autre téléphone"
        self.fields['additional_email'].label="E-mail"
        self.fields['lastregistration_choice'].label="Avez-vous déjà été inscrit à l\'UCL/Saint-Louis ?"
        self.fields['register_number'].label="Quel est votre numéro de matricule ? *"
        self.fields['ucl_last_year'].label="Quelle est votre dernière année à l\'UCL/Saint-Louis ? *"

    class Meta:
        model = Person
        exclude = ['activation_code']


class PersonLegalAddressForm(forms.ModelForm):
     prefix='l'
     type = forms.CharField(widget=forms.HiddenInput(), initial='LEGAL')
     def __init__(self, *args, **kwargs):
        super(PersonLegalAddressForm, self).__init__(*args, **kwargs)

        self.fields['postal_code'].help_text = "(ex: 1348)"
        self.fields['city'].help_text = "(ex: Louvain-la-Neuve)"

        self.fields['street'].label="Rue/Avenue"
        self.fields['number'].label="Numéro"
        self.fields['complement'].label="Lieu-dit (éventuellement)"
        self.fields['postal_code'].label="Code postal *"
        self.fields['city'].label="Localité *"
        self.fields['country'].label="Pays *"

     class Meta:
        model = PersonAddress
        exclude = ['person']


class PersonContactAddressForm(PersonLegalAddressForm):
     prefix='c'
     type = forms.CharField(widget=forms.HiddenInput(), initial='CONTACT')


class PersonAddressMatchingForm(forms.Form):

    ADDRESSMATCHING_CHOICES = (
        ('1', _('Oui')),
        ('2', _('Non')))

    addressMatching_choice = forms.ChoiceField(widget=forms.RadioSelect, choices=ADDRESSMATCHING_CHOICES, initial='2')

    def __init__(self, *args, **kwargs):
        super(PersonAddressMatchingForm, self).__init__(*args, **kwargs)
        self.fields['addressMatching_choice'].label="Adresse de contact est la même que votre domicile légal"
