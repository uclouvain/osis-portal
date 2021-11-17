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
import datetime
import json
import logging
from typing import Dict

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.exceptions import MultipleObjectsReturned
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _
from django.views.generic import TemplateView

from attestation.queues import student_attestation_status
from base.business import student as student_business
from base.models.person import Person
from base.models.student import Student
from dashboard.views import main as dash_main_view
from reference.services.academic_calendar import AcademicCalendarService

logger = logging.getLogger(settings.DEFAULT_LOGGER)
ATTESTATION_TYPE_ECHEANCE = "ECHEANCE"
PAYMENT_NOTICE_1_WARNING_REFERENCE = "PAYMENT_NOTICE_1_WARNING"


class Home(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    permission_required = 'base.is_student'
    template_name = 'attestation_home_student.html'

    @cached_property
    def person(self) -> Person:
        return self.request.user.person

    @cached_property
    def student(self) -> Student:
        return student_business.find_by_user_and_discriminate(self.request.user)

    def dispatch(self, request, *args, **kwargs):
        try:
            return super().dispatch(request, *args, **kwargs)
        except MultipleObjectsReturned:  # Exception raised by find_by_user_and_discriminate
            logger.exception('User {} returned multiple students.'.format(self.request.user.username))
            return dash_main_view.show_multiple_registration_id_error(self.request)

    def get_attestation_data(self) -> Dict:
        if self.student:
            json_message = _make_registration_json_message(self.student.registration_id)
            attestation_statuses_json_dict = student_attestation_status.fetch_json_attestation_statuses(json_message)
        else:
            attestation_statuses_json_dict = None
        return _make_attestation_data(attestation_statuses_json_dict, self.student, self.person)

    def get_context_data(self, **kwargs) -> Dict:
        return {
            **super().get_context_data(**kwargs),
            **self.get_attestation_data()
        }


def _make_registration_json_message(registration_id: str):
    json_message = None
    if registration_id:
        message = {'registration_id': registration_id}
        json_message = json.dumps(message)
    return json_message


def _make_attestation_data(attestation_statuses_all_years_json_dict: Dict, student: Student, person: Person) -> Dict:
    if attestation_statuses_all_years_json_dict:
        attestations = attestation_statuses_all_years_json_dict.get('attestationStatusesAllYears')
        current_year = attestation_statuses_all_years_json_dict.get('current_year')
        returned_registration_id = attestation_statuses_all_years_json_dict.get('registration_id')
        current_year_echeance_attestation = _get_current_year_echeance_attestation(attestations, current_year)
        display_warning_echeance_attestation_1 = _check_display_warning_echeance_attestation_1(
            data_year=current_year_echeance_attestation,
            person=person
        )
        if returned_registration_id != student.registration_id:
            raise Exception(_('Registration fetched doesn\'t match with student registration_id'))
    else:
        attestations = None
        current_year = None
        current_year_echeance_attestation = None
        display_warning_echeance_attestation_1 = False
    return {
        'attestations': attestations,
        'current_year': current_year,
        'student': student,
        'current_year_echeance_attestation': current_year_echeance_attestation,
        'attestation_type_echeance': ATTESTATION_TYPE_ECHEANCE,
        'display_warning_echeance_attestation_1': display_warning_echeance_attestation_1
    }


def _get_current_year_echeance_attestation(attestations, current_year):
    if attestations:
        current_year_attestations = next(
            (attestation for attestation in attestations if attestation["academicYear"] == current_year), None
        )
        if current_year_attestations:
            return next(
                (attestation for attestation in current_year_attestations['attestationStatuses'] if
                 attestation["attestationType"] == ATTESTATION_TYPE_ECHEANCE), None
            )
    return None


def _check_display_warning_echeance_attestation_1(data_year: int, person: Person) -> bool:
    acad_calendars_payment_notice_1_warning_api_response = AcademicCalendarService.get_academic_calendar_list(
        person=person,
        data_year=data_year,
        reference=PAYMENT_NOTICE_1_WARNING_REFERENCE
    )
    academic_calendars_payment_notice_1_warning = acad_calendars_payment_notice_1_warning_api_response.get('results')
    if academic_calendars_payment_notice_1_warning:
        today = datetime.date.today()
        for calendar in academic_calendars_payment_notice_1_warning:
            start_date = calendar.get('start_date')
            end_date = calendar.get('end_date')
            if start_date <= today and (end_date is None or end_date >= today):
                return True
    return False
