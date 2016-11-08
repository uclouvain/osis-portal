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
from localflavor.generic.forms import IBANFormField, BICFormField


class AccountingForm(forms.Form):
    scholarship = forms.BooleanField()
    scholarship_organization = forms.CharField()
    bank_account_iban = IBANFormField()
    bank_account_bic = BICFormField()

    def __init__(self, *args, **kwargs):
        super(AccountingForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super(AccountingForm, self).clean()
        data = cleaned_data.get('scholarship_organization')
        data_scholarship = cleaned_data.get('scholarship')
        if data_scholarship and (data is None or len(data) == 0):
            self.errors['scholarship_organization'] = _('mandatory_field')
        return cleaned_data