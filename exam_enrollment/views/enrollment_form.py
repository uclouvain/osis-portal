##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2022 Université catholique de Louvain (http://www.uclouvain.be)
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
import logging
import warnings
from datetime import datetime
from typing import Dict, List

import pika
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView
from osis_offer_enrollment_sdk.model.enrollment import Enrollment

import dashboard.views.home
from base.models.academic_year import current_academic_year
from base.models.person import Person
from base.models.student import Student
from base.services.offer_enrollment import OfferEnrollmentService, OfferEnrollmentBusinessException
from base.views import layout
from exam_enrollment.services.learning_unit_enrollment import LearningUnitEnrollmentService
from exam_enrollment.views.utils import get_request_timeout, get_exam_enroll_request, ask_queue_for_exam_enrollment_form
from frontoffice.settings.osis_sdk.utils import MultipleApiBusinessException
from osis_common.queue import queue_sender

logger = logging.getLogger(settings.DEFAULT_LOGGER)
queue_exception_logger = logging.getLogger(settings.QUEUE_EXCEPTION_LOGGER)


class ExamEnrollmentForm(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    permission_required = 'base.is_student'
    template_name = 'exam_enrollment_form.html'

    @cached_property
    def title(self) -> str:
        return self.offer_enrollment.title

    @property
    def program_code(self) -> str:
        return self.kwargs['acronym']

    @property
    def year(self) -> int:
        return int(self.kwargs['academic_year'])

    @cached_property
    def person(self) -> Person:
        return Person.objects.get(user=self.request.user)

    @cached_property
    def student(self) -> Student:
        if self.offer_enrollment:
            registration_id = self.offer_enrollment.student_registration_id
            return Student.objects.get(registration_id=registration_id)

    def dispatch(self, request, *args, **kwargs):
        try:
            return super().dispatch(request, *args, **kwargs)
        except MultipleApiBusinessException as e:
            for exception in e.exceptions:
                if exception.status_code == OfferEnrollmentBusinessException.DoubleNOMA.value:
                    return dashboard.views.home.show_multiple_registration_id_error(self.request)

    @cached_property
    def offer_enrollment(self) -> Enrollment:
        offer_enrollments = OfferEnrollmentService.get_my_enrollments_year_list(
            person=self.person, year=self.year
        )
        return next(
            (offer_enrollment for offer_enrollment in offer_enrollments
             if offer_enrollment.acronym == self.program_code),
            None
        )

    def post(self, *args, **kwargs):
        return self._process_exam_enrollment_form_submission()

    def _process_exam_enrollment_form_submission(self) -> HttpResponse:
        # Lines before data_to_submit = ... are temporary (covid-19)
        covid_choices = ['testwe_exam', 'moodle_exam', 'teams_exam']
        all_covid_choices_made = all(self.request.POST.get(choice) for choice in covid_choices)
        covid_period = self.request.POST.get('covid_period')
        if covid_period and not all_covid_choices_made:
            messages.add_message(self.request, messages.ERROR, _('Form not submitted !'))
            messages.add_message(
                self.request, messages.ERROR, _('Please complete IMPERATIVELY the questionnaire below')
            )
            return self._get_exam_enrollment_form()

        data_to_submit = _exam_enrollment_form_submission_message(
            self.request, self.student, self.program_code, self.year
        )

        queue_sender.send_message(
            settings.QUEUES.get('QUEUES_NAME').get('EXAM_ENROLLMENT_FORM_SUBMISSION'), data_to_submit
        )
        if covid_period:
            messages.add_message(self.request, messages.SUCCESS, _('exam_enrollment_form_submitted_covid_period'))
        else:
            messages.add_message(self.request, messages.SUCCESS, _('exam_enrollment_form_submitted'))
        return HttpResponseRedirect(reverse('dashboard_home'))

    def get(self, *args, **kwargs):
        return self._get_exam_enrollment_form()

    @cached_property
    def request_timeout(self) -> int:
        return get_request_timeout()

    def _get_exam_enrollment_form(self) -> HttpResponse:
        if not self.learning_unit_enrollments:
            messages.add_message(
                self.request,
                messages.WARNING,
                _('no_learning_unit_enrollment_found').format(self.program_code)
            )
            return HttpResponseRedirect(reverse('dashboard_home'))

        exam_enroll_request = get_exam_enroll_request(self.program_code, self.request_timeout, self.student)

        data = {}
        if exam_enroll_request:
            try:
                data = json.loads(exam_enroll_request.document)
            except json.JSONDecodeError:
                logger.exception("Json data is not valid")
        else:
            self.ask_exam_enrollment_form()
        return layout.render(self.request, self.template_name, self._get_context(data))

    @cached_property
    def learning_unit_enrollments(self) -> List[Enrollment]:
        return LearningUnitEnrollmentService.get_my_enrollments_list(
            program_code=self.program_code,
            year=self.year,
            person=self.person
        ).results

    def _get_context(self, data: Dict) -> Dict:
        return {
            'error_message': self._get_error_message(data),
            'exam_enrollments': data.get('exam_enrollments', ''),
            'student': self.student,
            'current_number_session': data.get('current_number_session', ''),
            'academic_year': current_academic_year(),
            'program_code': self.program_code,
            'title': self.title,
            'year': self.year,
            'request_timeout': self.request_timeout,
            'testwe_exam': data.get('testwe_exam'),
            'teams_exam': data.get('teams_exam'),
            'moodle_exam': data.get('moodle_exam'),
            'covid_period': data.get('covid_period'),
            'is_11ba': self.program_code.endswith('11BA'),
        }

    def _get_error_message(self, data: Dict) -> str:
        if data.get('error_message') == 'outside_exam_enrollment_period':
            error_message = _("You are outside the exams enrollment period.")
            exam_enrollment_date = data.get('exam_enrollment_date')
            if exam_enrollment_date:
                dt_obj = datetime.fromtimestamp(exam_enrollment_date).strftime('%d-%m-%Y')
                error_message += " {}".format(
                    _("The next registration period opens on %(next_exam_enrollment_date)s.") %
                    {'next_exam_enrollment_date': dt_obj}
                )

        elif data.get('error_message') == 'student_can_not_enrol_to_exam':
            error_message = _("You can not enrol to exam")
        elif data.get('error_message') == 'no_exam_enrollment_found':
            error_message = _("No exam enrollment found")
        elif data.get('error_message') == 'no_exam_enrollment_avalaible':
            error_message = _("Exam enrollment is not available")
        elif data.get('error_message'):
            error_message = _(data.get('error_message')).format(self.program_code)
        else:
            error_message = data.get('error_message')
        return error_message

    def ask_exam_enrollment_form(self) -> HttpResponse:
        if 'exam_enrollment' in settings.INSTALLED_APPS and hasattr(settings, 'QUEUES') and settings.QUEUES:
            try:
                message_published = ask_queue_for_exam_enrollment_form(self._exam_enrollment_form_message())
            except (
                    RuntimeError,
                    pika.exceptions.ConnectionClosed,
                    pika.exceptions.ChannelClosed,
                    pika.exceptions.AMQPError
            ):
                return HttpResponse(status=400)
            if message_published:
                return HttpResponse(status=200)
        return HttpResponse(status=405)

    def _exam_enrollment_form_message(self) -> Dict:
        return {
            'registration_id': self.student.registration_id,
            'offer_year_acronym': self.program_code,
            'year': self.year,
        }


def _exam_enrollment_form_submission_message(request, student: Student, program_code: str, year: int) -> Dict:
    return {
        'registration_id': student.registration_id,
        'offer_year_acronym': program_code,
        'year': year,
        'exam_enrollments': _build_enrollments_by_learning_unit(request),
        'testwe_exam': request.POST.get('testwe_exam'),
        'teams_exam': request.POST.get('teams_exam'),
        'moodle_exam': request.POST.get('moodle_exam')
    }


def _build_enrollments_by_learning_unit(request) -> List[Dict]:
    warnings.warn(
        "The field named 'etat_to_inscr' is only used to call EPC services. It should be deleted when the exam "
        "enrollment business will be implemented in Osis (not in EPC anymore). "
        "The flag 'is_enrolled' should be sufficient for Osis."
        "Do not forget to delete the hidden input field in the html template.",
        DeprecationWarning
    )
    enrollments_by_learn_unit = []
    is_enrolled_by_acronym = _build_dicts_is_enrolled_by_acronym(request)
    etat_to_inscr_by_acronym = _build_dicts_etat_to_inscr_by_acronym(request)

    for acronym, etat_to_inscr in etat_to_inscr_by_acronym.items():
        etat_to_inscr = None if not etat_to_inscr or etat_to_inscr == 'None' else etat_to_inscr
        if etat_to_inscr:
            enrollments_by_learn_unit.append({
                'acronym': acronym,
                'is_enrolled': is_enrolled_by_acronym.get(acronym, False),
                'etat_to_inscr': etat_to_inscr
            })
    return enrollments_by_learn_unit


def _build_dicts_is_enrolled_by_acronym(request) -> Dict:
    current_number_session = request.POST['current_number_session']
    return {
        _extract_acronym(html_tag_id): True if value == "on" else False
        for html_tag_id, value in request.POST.items()
        if "chckbox_exam_enrol_sess{}_".format(current_number_session) in html_tag_id
    }


def _build_dicts_etat_to_inscr_by_acronym(request) -> Dict:
    return {
        _extract_acronym(html_tag_id): etat_to_inscr
        for html_tag_id, etat_to_inscr in request.POST.items()
        if "etat_to_inscr_current_session_" in html_tag_id
    }


def _extract_acronym(html_tag_id: str) -> str:
    return html_tag_id.split("_")[-1]
