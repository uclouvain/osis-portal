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
from django.utils.translation import gettext_lazy as _


class OfferPreferenceForm(forms.Form):
    PREFERENCE_CHOICES = (
        ('0', '--'),
        ('1', _('First choice')),
        ('2', _('Second choice')),
        ('3', _('Third choice')),
        ('4', _('Fourth choice'))
    )
    offer = forms.IntegerField()
    preference = forms.ChoiceField(choices=PREFERENCE_CHOICES, required=True)


class OfferPreferenceFormSet(forms.BaseFormSet):
    def clean(self):
        if any(self.errors):
            return

        preferences_made = {}
        offers_selected = {}
        for form in self.forms:
            preference = form.cleaned_data['preference']
            offer = form.cleaned_data['offer']
            if not int(preference):
                continue
            preferences_made[preference] = preferences_made.get(preference, 0) + 1
            offers_selected[offer] = offers_selected.get(offer, 0) + 1
            if preferences_made[preference] > 1:
                raise forms.ValidationError(_("Cannot apply same preference on distinct offers"))
            if offers_selected[offer] > 1:
                raise forms.ValidationError(_("Cannot select same offer"))
