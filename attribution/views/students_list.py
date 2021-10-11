##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2021 Université catholique de Louvain (http://www.uclouvain.be)
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
import json
from typing import List, Union, Dict

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.functional import cached_property
from django.views.generic import TemplateView
from osis_learning_unit_enrollment_sdk.model.student_specific_profile import StudentSpecificProfile

from attribution.business import xls_students_by_learning_unit
from attribution.services.attribution import AttributionService
from attribution.services.enrollments import LearningUnitEnrollmentService
from attribution.services.learning_unit import LearningUnitService
from frontoffice.settings.osis_sdk.utils import ApiPaginationMixin, ApiRetrieveAllObjectsMixin
from osis_common.utils.models import get_object_or_none
from performance.models.student_performance import StudentPerformance

JSON_LEARNING_UNIT_NOTE = 'note'
JSON_LEARNING_UNIT_STATUS = 'etatExam'
JANUARY = "janvier"
JUNE = "juin"
SEPTEMBER = "septembre"

EnrollmentDict = Dict[str, Union[str, StudentSpecificProfile]]


class StudentsListView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView, ApiPaginationMixin):
    permission_required = "base.can_access_attribution"
    template_name = "students_list.html"
    api_call = LearningUnitEnrollmentService.get_enrollments_paginated_list

    def get(self, *args, **kwargs):
        # default ordering by program and student_last_name if no ordering parameter (trigger filter tags)
        if not self.request.GET.get('ordering'):
            return redirect(self.request.get_full_path() + "?ordering=program,student_last_name")
        return super().get(self, *args, **kwargs)

    @property
    def is_class(self):
        return bool(self.kwargs.get('class_code'))

    @property
    def code(self):
        return self.effective_class.full_code if self.is_class else self.kwargs['learning_unit_acronym']

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            'global_id': self.request.user.person.global_id,
            'students': self.enrollments_list,
            'learning_unit_year': int(self.kwargs['learning_unit_year']),
            'learning_unit_acronym': self.code,
            'learning_unit_title': self.learning_unit_title,
            # TODO:  provide endpoint to check luy has_peps
            'has_peps': self.has_peps_student(),
            'produce_xls_url': self.get_produce_xls_url(),
            'count': self.count,
            'enrolled_students_count': self.paginated_response.get_extra('enrolled_students_count')
        }

    @cached_property
    def learning_unit_title(self):
        return self._get_learning_class_title() if self.is_class else self._get_learning_unit_title()

    def _get_learning_unit_title(self):
        return LearningUnitService.get_learning_unit_title(
            acronym=self.kwargs['learning_unit_acronym'],
            year=int(self.kwargs['learning_unit_year']),
            person=self.request.user.person
        )

    @cached_property
    def effective_class(self):
        classes = LearningUnitService.get_effective_classes(
            acronym=self.kwargs['learning_unit_acronym'],
            year=int(self.kwargs['learning_unit_year']),
            person=self.request.user.person
        )
        return next(
            (
                effective_class for effective_class in classes
                if effective_class.code == self.kwargs['class_code']
            ),
            None
        )

    def _get_learning_class_title(self):
        return self.effective_class.title_fr if self.effective_class else ''

    def get_api_kwargs(self):
        return {
            **super().get_api_kwargs(),
            'year': int(self.kwargs['learning_unit_year']),
            'acronym': "{}{}".format(self.kwargs['learning_unit_acronym'], self.kwargs.get('class_code', "")),
        }

    @cached_property
    def enrollments_list(self) -> List[EnrollmentDict]:
        return list(map(self.get_enrollments_dict_for_display, super().page_objects_list))

    def get_enrollments_dict_for_display(self, enrollment) -> EnrollmentDict:
        session_results = self.get_sessions_results(enrollment)
        note_september = self.get_session_value(session_results, SEPTEMBER, JSON_LEARNING_UNIT_NOTE)
        note_june = self.get_session_value(session_results, JUNE, JSON_LEARNING_UNIT_NOTE)
        note_january = self.get_session_value(session_results, JANUARY, JSON_LEARNING_UNIT_NOTE)
        last_note = None
        if note_september != "-":
            last_note = note_september
        elif note_june != "-":
            last_note = note_june
        elif note_january != "-":
            last_note = note_january
        return {
            'name': "{0}, {1}".format(
                enrollment.student_last_name.upper(),
                enrollment.student_first_name
            ),
            'email': enrollment.student_email,
            'program': enrollment.program,
            'acronym': enrollment.learning_unit_acronym,
            'registration_id': enrollment.student_registration_id,
            'january_note': self.get_session_value(session_results, JANUARY, JSON_LEARNING_UNIT_NOTE),
            'january_status': self.get_session_value(session_results, JANUARY, JSON_LEARNING_UNIT_STATUS),
            'june_note': self.get_session_value(session_results, JUNE, JSON_LEARNING_UNIT_NOTE),
            'june_status': self.get_session_value(session_results, JUNE, JSON_LEARNING_UNIT_STATUS),
            'september_note': self.get_session_value(session_results, SEPTEMBER, JSON_LEARNING_UNIT_NOTE),
            'september_status': self.get_session_value(session_results, SEPTEMBER, JSON_LEARNING_UNIT_STATUS),
            'student_specific_profile': enrollment.specific_profile,
            'last_note': last_note
        }

    def get_sessions_results(self, enrollment):
        a_registration_id = enrollment.student_registration_id
        offer_acronym = enrollment.program
        academic_year = self.kwargs['learning_unit_year']

        results = {}
        a_student_performance = get_object_or_none(
            StudentPerformance,
            registration_id=a_registration_id,
            academic_year=academic_year,
            acronym=offer_acronym
        )

        if a_student_performance:
            student_data = self.get_student_data_dict(a_student_performance)
            monAnnee = student_data['monAnnee']
            if student_data['etudiant']['noma'] == a_registration_id and monAnnee['anac'] == academic_year:
                monOffre = monAnnee['monOffre']
                offre = monOffre['offre']
                if offre['sigleComplet'] == offer_acronym:
                    cours_list = monOffre['cours']
                    self.manage_cours_list(cours_list, results)
        return results

    @staticmethod
    def get_student_data_dict(a_student_performance):
        try:
            data_input = json.dumps(a_student_performance.data)
            return json.loads(data_input)
        except (AttributeError, ValueError):
            return None

    def manage_cours_list(self, cours_list, results):
        if cours_list:
            nb_cours = 0
            while nb_cours < len(cours_list):
                cours = cours_list[nb_cours]
                if cours['sigleComplet'] == self.kwargs['learning_unit_acronym']:
                    self.get_student_results(cours, results)
                nb_cours = nb_cours + 1

    def get_student_results(self, cours, results):
        sessions = cours['session']
        nb_session = 0
        while nb_session < len(sessions):
            results.update({
                sessions[nb_session]['mois']: {
                    JSON_LEARNING_UNIT_NOTE: self.get_value(sessions[nb_session], JSON_LEARNING_UNIT_NOTE),
                    JSON_LEARNING_UNIT_STATUS: self.get_value(sessions[nb_session], JSON_LEARNING_UNIT_STATUS)
                }
            })
            nb_session = nb_session + 1

    @staticmethod
    def get_value(session, variable_name):
        try:
            return session[variable_name]
        except KeyError:
            return None

    @staticmethod
    def get_session_value(session_results, month_session, variable_to_get):
        try:
            return session_results[month_session][variable_to_get]
        except KeyError:
            return None

    def has_peps_student(self):
        attributions = AttributionService.get_attributions_list(
            year=int(self.kwargs['learning_unit_year']),
            person=self.request.user.person,
            with_effective_class_repartition=True
        )

        attribution = next((a for a in attributions if a['code'] == self.kwargs['learning_unit_acronym']), None)
        if attribution and self.is_class:
            effective_class = next(
                (e for e in attribution['effective_class_repartition'] if e['code'][-1] == self.kwargs['class_code']),
                None
            )
            return bool(effective_class) and effective_class['has_peps']
        return bool(attribution) and attribution['has_peps']

    def get_produce_xls_url(self):
        return reverse('produce_xls_students', kwargs={
            'learning_unit_acronym': self.kwargs['learning_unit_acronym'],
            'learning_unit_year': self.kwargs['learning_unit_year']
        })


class AdminStudentsListView(StudentsListView):
    permission_required = "base.is_faculty_administrator"
    template_name = "students_list_admin.html"


class StudentsListXlsView(StudentsListView, ApiRetrieveAllObjectsMixin):
    permission_required = "base.can_access_attribution"
    api_call = LearningUnitEnrollmentService.get_all_enrollments_list
    ordering = 'program,student_last_name'

    def get(self, *args, **kwargs):
        student_list = self.enrollments_list
        return xls_students_by_learning_unit.get_xls(
            student_list,
            self.kwargs['learning_unit_acronym'],
            self.kwargs['learning_unit_year']
        )
