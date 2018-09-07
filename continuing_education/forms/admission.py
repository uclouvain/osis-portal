from django.forms import ModelForm

from base.models import offer_year
from continuing_education.models.admission import Admission
from django.utils.translation import ugettext_lazy as _
from django import forms

class FormationChoiceField(forms.ModelChoiceField):
    def label_from_instance(obj):
        return "{} - {}".format(obj.acronym, obj.title)

class FacultyChoiceField(forms.ModelChoiceField):
    def label_from_instance(obj):
        return "{}".format(obj.acronym)

class AdmissionForm(ModelForm):
    high_school_diploma = forms.TypedChoiceField(coerce=lambda x: x =='True',
                                   choices=((False, _('No')), (True, _('Yes'))), label=_("high_school_diploma"))

    def __init__(self, *args, **kwargs):
        super(AdmissionForm, self).__init__(*args, **kwargs)
        self.fields['formation'].label_from_instance = FormationChoiceField.label_from_instance
        self.fields['faculty'].label_from_instance = FacultyChoiceField.label_from_instance
        # avoid adding META ordering in OfferYear model
        self.fields['formation'].queryset = self.fields['formation'].queryset.all().order_by('acronym')

    class Meta:
        model = Admission
        fields = [
            'first_name',
            'last_name',
            'birth_date',
            'birth_location',
            'birth_country',
            'citizenship',
            'gender',
            # Contact
            'phone_mobile',
            'email',
            # Address
            'location',
            'postal_code',
            'city',
            'country',
            # Education
            'high_school_diploma',
            'high_school_graduation_year',
            'last_degree_level',
            'last_degree_field',
            'last_degree_institution',
            'last_degree_graduation_year',
            'other_educational_background',
            # Professional Background
            'professional_status',
            'current_occupation',
            'current_employer',
            'activity_sector',
            'past_professional_activities',
            # Motivation
            'motivation',
            'professional_impact',
            # Formation
            'formation',
            'courses_formula',
            'program_code',
            'faculty',
            'formation_administrator',
            # Awareness
            'awareness_ucl_website',
            'awareness_formation_website',
            'awareness_press',
            'awareness_facebook',
            'awareness_linkedin',
            'awareness_customized_mail',
            'awareness_emailing',
            # State
            'state',
        ]
        #automatic translation of field names
        labels = {field : _(field) for field in fields}