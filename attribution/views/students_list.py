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
from operator import itemgetter
from typing import List, Dict

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import TemplateView

from attribution.business import xls_students_by_learning_unit
from attribution.services.enrollments import LearningUnitEnrollmentService
from attribution.services.learning_unit import LearningUnitService
from performance.models import student_performance

JSON_LEARNING_UNIT_NOTE = 'note'
JSON_LEARNING_UNIT_STATUS = 'etatExam'
JANUARY = "janvier"
JUNE = "juin"
SEPTEMBER = "septembre"


class StudentsListView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    permission_required = "base.can_access_attribution"
    template_name = "students_list.html"

    def get_context_data(self, **kwargs):
        enrollments = self.get_learning_unit_yr_enrollments_list()
        return {
            **super().get_context_data(**kwargs),
            'global_id': self.request.user.person.global_id,
            'students': enrollments,
            'learning_unit_year': self.get_learning_unit(),
            'has_peps': self.has_peps_student(enrollments),
        }

    def get_learning_unit(self):
        return LearningUnitService.get_learning_unit(
            acronym=self.kwargs['learning_unit_acronym'],
            year=self.kwargs['learning_unit_year'],
            person=self.request.user.person
        )

    def get_learning_unit_yr_enrollments_list(self) -> List[Dict]:
        enrollments_paginated_response = LearningUnitEnrollmentService.get_enrollments_list(
            year=int(self.kwargs['learning_unit_year']),
            acronym=self.kwargs['learning_unit_acronym'],
            person=self.request.user.person,
        )
        enrollments = [
            self.get_enrollments_dict_for_display(enrollment)
            for enrollment in enrollments_paginated_response.results
        ]
        return sorted(enrollments, key=itemgetter('program'))

    def get_enrollments_dict_for_display(self, enrollment):
        session_results = self.get_sessions_results(enrollment)

        return {
            'name': "{0}, {1}".format(
                enrollment.student_first_name,
                enrollment.student_last_name
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
            'student_specific_profile': enrollment.specific_profile
        }

    def get_sessions_results(self, enrollment):
        a_registration_id = enrollment.student_registration_id
        offer_acronym = enrollment.program
        academic_year = self.kwargs['learning_unit_year']

        results = {}
        a_student_performance = student_performance.find_by_student_and_offer_year(
            a_registration_id, academic_year, offer_acronym
        )

        if a_student_performance:
            student_data = self.get_student_data_dict(a_student_performance)
            monAnnee = student_data['monAnnee']
            if student_data['etudiant']['noma'] == a_registration_id and monAnnee['anac'] == str(academic_year):
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

    @staticmethod
    def has_peps_student(enrollments):
        for enrollment in enrollments:
            if enrollment.get('student_specific_profile'):
                return True
        return False


class AdminStudentsListView(StudentsListView):
    permission_required = "base.is_faculty_administrator"
    template_name = "students_list_admin.html"


class StudentsListXlsView(StudentsListView):
    permission_required = "base.can_access_attribution"

    def get(self, *args, **kwargs):
        a_learning_unit_yr = LearningUnitService.get_learning_unit(
            acronym=self.kwargs['learning_unit_acronym'],
            year=self.kwargs['learning_unit_year'],
            person=self.request.user.person
        )
        student_list = self.get_learning_unit_yr_enrollments_list()
        return xls_students_by_learning_unit.get_xls(student_list, a_learning_unit_yr)
