##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2020 Université catholique de Louvain (http://www.uclouvain.be)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
from typing import List

from base.models.enums import learning_unit_enrollment_state, offer_enrollment_state
from base.tests.factories.learning_unit_year import LearningUnitYearFactory
from base.tests.factories.offer_enrollment import OfferEnrollmentFactory


class LearningUnitEnrollmentSerialized(dict):

    def __init__(self, learning_unit_year=None, offer_enrollment=None, learn_unit_enrol_state=None):
        super(LearningUnitEnrollmentSerialized, self).__init__()
        learning_unit_year = learning_unit_year or LearningUnitYearFactory()
        offer_enrollment = offer_enrollment or OfferEnrollmentFactory()
        self.update({
            "registration_id": offer_enrollment.student.registration_id,
            "student_first_name": offer_enrollment.student.person.first_name,
            "student_last_name": offer_enrollment.student.person.last_name,
            "student_email": offer_enrollment.student.person.email,
            "learning_unit_acronym": learning_unit_year.acronym,
            "education_group_acronym": offer_enrollment.offer_year.acronym,
            "academic_year": learning_unit_year.academic_year.year,
            "education_group_url": "https//...",
            "learning_unit_url": "https//...",
            "learning_unit_enrollment_state": learn_unit_enrol_state or learning_unit_enrollment_state.ENROLLED,
            "offer_enrollment_state": offer_enrollment_state.SUBSCRIBED,
        })


class APIResponseFactory(dict):

    serializer_klass = None

    def __init__(self, results_to_produce=1, results: List[dict] = None):
        assert self.serializer_klass is not None
        super(APIResponseFactory, self).__init__()
        self.update({
            'count': len(results) if results is not None else results_to_produce,
            'results': results or [self.serializer_klass() for _ in range(results_to_produce)]
        })


class LearningUnitEnrollmentAPIResponse(APIResponseFactory):
    serializer_klass = LearningUnitEnrollmentSerialized
