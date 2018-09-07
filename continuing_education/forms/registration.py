from django.forms import ModelForm

from continuing_education.models.admission import Admission
from django.utils.translation import ugettext_lazy as _
from django import forms

class RegistrationForm(ModelForm):
    previous_ucl_registration = forms.TypedChoiceField(coerce=lambda x: x =='True',
                                   choices=((False, _('No')), (True, _('Yes'))))
    class Meta:
        model = Admission
        fields = [
            'registration_type',
            'use_address_for_billing',
            'billing_location',
            'billing_postal_code',
            'billing_city',
            'billing_country',
            'head_office_name',
            'company_number',
            'vat_number',
            'national_registry_number',
            'id_card_number',
            'passport_number',
            'marital_status',
            'spouse_name',
            'children_number',
            'previous_ucl_registration',
            'previous_noma',
            'use_address_for_post',
            'residence_location',
            'residence_postal_code',
            'residence_city',
            'residence_country',
            'residence_phone',
            'registration_complete',
            'noma',
            'payment_complete',
            'formation_spreading',
            'prior_experience_validation',
            'assessment_presented',
            'assessment_succeeded',
            'sessions'
        ]
        labels = {}
        for field in fields:
            labels[field] = _(field)
            if "billing_" in field:
                labels[field] = _(field.replace("billing_",''))
            if "residence_" in field:
                labels[field] = _(field.replace("residence_",''))

