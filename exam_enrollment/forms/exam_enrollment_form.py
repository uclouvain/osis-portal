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


class Session:
    def __init__(self, *args, **kwargs):
        self.score = kwargs.get('score')
        self.enrollment_state = kwargs.get('enrollment_state')


class LearningUnitYear:
    def __init__(self, *args, **kwargs):
        self.acronym = kwargs.get('acronym')
        self.title = kwargs.get('title')
        self.enrollment_state = kwargs.get('enrollment_state')


class ExamEnrollmentForm(forms.Form):
    # Un form doit-il avoir obligatoirement des fields qui seront édités ?
    # Ou bien peuvent-il avoir des field servant uniquement à l'affichage?

    def __init__(self, *args, **kwargs):
        initial = kwargs.get('initial')
        if initial:
            initials = dict(initial)
            cpy = dict(initials)
            self.credits = initials.pop('credits')
            self.credited = initials.pop('credited')
            self.enrolled_by_default = initials.pop('enrolled_by_default', False)
            self.etat_to_inscr_current_session = initials.pop('etat_to_inscr_current_session')
            self.is_enrolled = forms.BooleanField(required=False, initial=self.enrolled_by_default)
            self.session_1 = Session(**initials.pop('session_1', {}))
            self.session_2 = Session(**initials.pop('session_2', {}))
            self.session_3 = Session(**initials.pop('session_3', {}))
            self.learning_unit_year = LearningUnitYear(**initials.pop('learning_unit_year'))
            super(ExamEnrollmentForm, self).__init__(*args, **kwargs)
            kwargs['initial'] = cpy # Used for nexts forms in Formset
        else:
            super(ExamEnrollmentForm, self).__init__(*args, **kwargs)


# class ExamEnrollmentFormSet:
#     def __init__(self, *args, **kwargs):
#         self.registration_id = kwargs.pop('registration_id')
#         self.current_number_session = kwargs.pop('current_number_session')
#         self.forms = [ExamEnrollmentForm(**exam_enrol) for exam_enrol in kwargs.get('exam_enrollments')]


# class ExamEnrollmentFormSet(forms.BaseFormSet):
#     def __init__(self, *args, **kwargs):
#         self.registration_id = kwargs.pop('registration_id')
#         self.current_number_session = kwargs.pop('current_number_session')
#         super(ExamEnrollmentFormSet, self).__init__(*args, **kwargs)
    # def add_fields(self, form, index):
    #     super(ExamEnrollmentFormSet, self).add_fields(form, index)
    #     form.fields["my_field"] = forms.CharField()
