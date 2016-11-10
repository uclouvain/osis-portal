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


class NewAccountForm(forms.Form):
    first_name_new = forms.CharField(required=True, max_length=30)
    last_name_new = forms.CharField(required=True, max_length=30)
    email_new = forms.EmailField(required=True)
    email_new_confirm = forms.EmailField(required=True)
    password_new = forms.CharField(widget=forms.PasswordInput, required=True)
    password_new_confirm = forms.CharField(widget=forms.PasswordInput, required=True)
    verification = forms.CharField(required=True, label=_(''))

    def __init__(self, *args, **kwargs):
        super(NewAccountForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super(NewAccountForm, self).clean()
        email_new = cleaned_data.get("email_new")
        email_new_confirm = cleaned_data.get("email_new_confirm")
        if email_new != email_new_confirm:
            self.errors['email_new_confirm'] = _('different_emails')

        password_new = cleaned_data.get("password_new")
        password_new_confirm = cleaned_data.get("password_new_confirm")
        if password_new != password_new_confirm:
            self.errors['password_new_confirm'] = _('different_passwords')
        if password_new and len(password_new) < 8:
            self.errors['password_new'] = _('password_too_short')
        return cleaned_data

    def clean_password_new(self):
        data = self.cleaned_data['password_new']
        return data.strip()

    def clean_password_new_confirm(self):
        data = self.cleaned_data['password_new_confirm']
        return data.strip()


class AccountForm(forms.Form):
    email = forms.EmailField(required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)

    def __init__(self, *args, **kwargs):
        super(AccountForm, self).__init__(*args, **kwargs)

    def clean_email(self):
        data = self.cleaned_data['email']
        if data is None or len(data) == 0:
            self.errors['email'] = _('mandatory_field')
        return data.strip()

    def clean_password(self):
        data = self.cleaned_data['password']
        return data.strip()


class NewPasswordForm(forms.Form):
    password_new = forms.CharField(widget=forms.PasswordInput, required=True)
    password_new_confirm = forms.CharField(widget=forms.PasswordInput, required=True)

    def __init__(self, *args, **kwargs):
        super(NewPasswordForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super(NewPasswordForm, self).clean()
        password_new = cleaned_data.get("password_new")
        password_new_confirm = cleaned_data.get("password_new_confirm")
        if password_new != password_new_confirm:
            self.errors['password_new_confirm'] = _('different_passwords')
        if password_new and len(password_new) < 8:
            self.errors['password_new'] = _('password_too_short')
        return cleaned_data

    def clean_password_new(self):
        data = self.cleaned_data['password_new']
        return data.strip()

    def clean_password_new_confirm(self):
        data = self.cleaned_data['password_new_confirm']
        return data.strip()


class AccessAccountForm(forms.Form):
    email = forms.EmailField(required=True)

    def __init__(self, *args, **kwargs):
        super(AccessAccountForm, self).__init__(*args, **kwargs)

    def clean_email(self):
        data = self.cleaned_data['email']
        if data is None or len(data) == 0:
            self.errors['email'] = _('mandatory_field')
        return data.strip()