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
from admission.models import sociological_survey as mdl_sociological_survey, profession as mdl_profession
from admission.models.enums import professional_activity
from admission.models.enums import education as education_enum, professional_activity as prof_activity_enum


class SociologicalSurveyForm(forms.ModelForm):

    number_brothers_sisters = forms.IntegerField(required=False, initial=0)
    mother_profession_not_found = forms.BooleanField(initial=False, required=False)
    mother_profession_other_name = forms.CharField(initial=None,required=False)
    father_profession_not_found = forms.BooleanField(initial=False, required=False)
    father_profession_other_name = forms.CharField(initial=None,required=False)
    student_profession_not_found = forms.BooleanField(initial=False, required=False)
    student_profession_other_name = forms.CharField(initial=None,required=False)
    conjoint_profession_not_found = forms.BooleanField(initial=False, required=False)
    conjoint_profession_other_name = forms.CharField(initial=None,required=False)
    paternal_grandfather_profession_not_found = forms.BooleanField(initial=False, required=False)
    paternal_grandfather_profession_other_name = forms.CharField(initial=None, required=False)
    maternal_grandfather_profession_not_found = forms.BooleanField(initial=False, required=False)
    maternal_grandfather_profession_other_name = forms.CharField(initial=None,required=False)

    class Meta:
        model = mdl_sociological_survey.SociologicalSurvey
        exclude = ['applicant']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.education_types = education_enum.EDUCATION_TYPE_CHOICES
        self.professions = list(mdl_profession.find_distinct_by_adoc(False))
        self.proffessional_activities = prof_activity_enum.PROFESSIONAL_ACTIVITY_CHOICES
        self.__init_other_profession_not_found('student_profession')
        self.__init_other_profession_not_found('mother_profession')
        self.__init_other_profession_not_found('father_profession')
        self.__init_other_profession_not_found('conjoint_profession')
        self.__init_other_profession_not_found('paternal_grandfather_profession')
        self.__init_other_profession_not_found('maternal_grandfather_profession')

    def __init_other_profession_not_found(self, field_name):
        if self.fields[field_name]:
            profession = mdl_profession.find_by_id(self.initial.get(field_name))
            if profession and profession.adhoc:
                self.initial[''.join([field_name,'_not_found'])] = True
                self.initial[''.join([field_name,'_other_name'])] = profession.name
            else:
                self.initial[''.join([field_name,'_not_found'])] = False
                self.initial[''.join([field_name,'_other_name'])] = None

    def save(self, applicant, commit=True):
        instance = super(SociologicalSurveyForm, self).save(commit=False)
        if commit:
            instance.applicant = applicant
            self._clean_all_professions(instance)
            instance.save()
        return instance

    def _clean_all_professions(self, instance):
         instance.student_profession = self._get_or_other_student_profession()
         instance.father_profession = self._get_or_other_father_profession()
         instance.mother_profession = self._get_or_other_mother_profession()
         instance.conjoint_profession = self._get_or_other_conjoint_profession()
         instance.paternal_grandfather_profession = self._get_or_other_paternal_grandfather_profession()
         instance.maternal_grandfather_profession = self._get_or_other_maternal_grandfather_profession()

    def _get_or_other_student_profession(self):
         return self.__profession_with_other_value('student_profession')

    def _get_or_other_father_profession(self):
        return self.__profession_with_other_value('father_profession')

    def _get_or_other_mother_profession(self):
        return self.__profession_with_other_value('mother_profession')

    def _get_or_other_conjoint_profession(self):
        return self.__profession_with_other_value('conjoint_profession')

    def _get_or_other_paternal_grandfather_profession(self):
        return self.__profession_with_other_value('paternal_grandfather_profession')

    def _get_or_other_maternal_grandfather_profession(self):
        return self.__profession_with_other_value('maternal_grandfather_profession')

    def __profession_with_other_value(self, field_name):
        if (not self[field_name].html_name in self.data or not self.data.get(self[field_name].html_name)) \
                and self.cleaned_data.get(field_name) is None \
                and self.cleaned_data.get(''.join([field_name,'_not_found'])):
            if self.cleaned_data.get(''.join([field_name,'_other_name'])):
                new_profession = mdl_profession.find_by_name(self.cleaned_data.get(''.join([field_name,'_other_name'])))
                if not new_profession:
                    new_profession = mdl_profession.Profession(name=self.cleaned_data.get(''.join([field_name,'_other_name'])),
                                                               adhoc=True)
                    new_profession.save()
                self.cleaned_data[field_name] = new_profession
        return self.cleaned_data.get(field_name)

    def clean_number_brothers_sisters(self):
        if not self['number_brothers_sisters'].html_name in self.data or \
                        self.cleaned_data.get('number_brothers_sisters') is None:
            return self.fields['number_brothers_sisters'].initial
        return self.cleaned_data.get('number_brothers_sisters')

    def clean(self):
        cleaned_data = super(SociologicalSurveyForm, self).clean()

        #  The user must filled either both or neither professional activity and profession
        student_professional_activity = cleaned_data.get('student_professional_activity')
        student_profession = cleaned_data.get('student_profession')
        student_profession_other_name = cleaned_data.get('student_profession_other_name')

        if student_profession is None and not student_profession_other_name and student_professional_activity is not None:
            if professional_activity.NO_PROFESSION != student_professional_activity:
                self.add_error('student_profession', _('field_is_required'))
        if (student_profession is not None or student_profession_other_name) and \
                (student_professional_activity is None
                 or professional_activity.NO_PROFESSION == student_professional_activity):
            self.add_error('student_professional_activity', _('field_is_required'))

        conjoint_professional_activity = cleaned_data.get('conjoint_professional_activity')
        conjoint_profession = cleaned_data.get('conjoint_profession')
        conjoint_profession_other_name = cleaned_data.get('conjoint_profession_other_name')
        if conjoint_profession is None and not conjoint_profession_other_name and conjoint_professional_activity is not None:
            if professional_activity.NO_PROFESSION != conjoint_professional_activity:
                self.add_error('conjoint_profession', _('field_is_required'))
        if (conjoint_profession is not None or conjoint_profession_other_name) and \
                (conjoint_professional_activity is None
                 or professional_activity.NO_PROFESSION == conjoint_professional_activity):
            self.add_error('conjoint_professional_activity', _('field_is_required'))
        return cleaned_data