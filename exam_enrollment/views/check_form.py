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
import logging

from django.conf import settings
from django.http import HttpResponse
from django.utils import timezone
from django.utils.functional import cached_property
from django.views import View
from osis_offer_enrollment_sdk.model.enrollment import Enrollment

from base.business import student as student_business
from base.models.student import Student
from base.services.offer_enrollment import OfferEnrollmentService
from exam_enrollment.models import exam_enrollment_request

logger = logging.getLogger(settings.DEFAULT_LOGGER)
queue_exception_logger = logging.getLogger(settings.QUEUE_EXCEPTION_LOGGER)


class CheckForm(View):

    @property
    def program_code(self) -> str:
        return self.kwargs['acronym']

    @property
    def year(self) -> int:
        return int(self.kwargs['academic_year'])

    @cached_property
    def student(self) -> Student:
        return student_business.find_by_user_and_discriminate(self.request.user)

    @cached_property
    def offer_enrollment(self) -> Enrollment:
        offer_enrollments = OfferEnrollmentService.get_enrollments_year_list(
            registration_id=self.student.registration_id,
            person=self.student.person,
            year=self.year
        ).results
        return next(
            (offer_enrollment for offer_enrollment in offer_enrollments
             if offer_enrollment.acronym == self.program_code),
            None
        )

    def get(self, *args, **kwargs):
        if 'exam_enrollment' in settings.INSTALLED_APPS:
            if self._exam_enrollment_up_to_date_in_db_with_document():
                return HttpResponse(status=200)
            else:
                return HttpResponse(status=404)
        return HttpResponse(status=405)

    def _exam_enrollment_up_to_date_in_db_with_document(self):
        if self.offer_enrollment:
            if hasattr(settings, 'QUEUES') and settings.QUEUES:
                request_timeout = settings.QUEUES.get("QUEUES_TIMEOUT").get("EXAM_ENROLLMENT_FORM_RESPONSE")
            else:
                request_timeout = settings.DEFAULT_QUEUE_TIMEOUT
            fetch_date_limit = timezone.now() - timezone.timedelta(seconds=request_timeout)
            exam_enroll_request = exam_enrollment_request.get_by_student_and_offer_year_acronym_and_fetch_date(
                self.student, self.program_code, fetch_date_limit
            )
            return exam_enroll_request and exam_enroll_request.document
        else:
            logger.warning("This student is not enrolled in this offer_year")
            return False
