##############################################################################
#
# OSIS stands for Open Student Information System. It's an application
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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
import random
import uuid

from django.test import TestCase, override_settings
from osis_internship_sdk.api.internship_api import InternshipApi
from osis_internship_sdk.model.score_list_get import ScoreListGet
from osis_internship_sdk.model.student import Student
from osis_internship_sdk.models import MasterGet, AllocationGet, PeriodGet, SpecialtyGet, OrganizationGet, \
    StudentAffectationGet, CohortGet, ScoreGet

from internship.models.enums.role_choice import ChoiceRole
from internship.services.api_client import InternshipAPIClient


class TestAPIClient(TestCase):

    @override_settings(OSIS_INTERNSHIP_SDK_HOST='test_url')
    def test_new_internship_api_client(self):
        api = InternshipAPIClient()
        self.assertEqual(api.api_client.configuration.host, 'test_url')


class MockAPI(InternshipApi):
    @classmethod
    def masters_get(*args, **kwargs):
        return {'count': 1, 'results': [MasterGet(uuid=str(uuid.uuid4()))]}

    @classmethod
    def masters_post(*args, **kwargs):
        return MasterGet()

    @classmethod
    def masters_uuid_allocations_get(*args, **kwargs):
        return {'count': 1, 'results': [AllocationGet(
            uuid=str(uuid.uuid4()),
            organization=OrganizationGet(uuid=str(uuid.uuid4()), reference=''),
            specialty=SpecialtyGet(uuid=str(uuid.uuid4()), acronym=''),
            role=ChoiceRole.MASTER.name,
        )]}

    @classmethod
    def periods_get(*args, **kwargs):
        return {'count': 1, 'results': [PeriodGet(uuid=str(uuid.uuid4()), name='P1')]}

    @classmethod
    def specialties_uuid_get(*args, **kwargs):
        return SpecialtyGet(uuid=str(uuid.uuid4()), cohort=CohortGet(uuid=str(uuid.uuid4())), acronym='')

    @classmethod
    def organizations_uuid_get(*args, **kwargs):
        return OrganizationGet(uuid=str(uuid.uuid4()), reference='')

    @classmethod
    def students_affectations_specialty_organization_get(*args, **kwargs):
        affectation = StudentAffectationGet(
            uuid=str(uuid.uuid4()),
            student=Student(uuid=str(uuid.uuid4()), last_name='', first_name=''),
            period=PeriodGet(uuid=str(uuid.uuid4()), name='P1')
        )
        return {'count': 1, 'results': [affectation], 'next': 'next_url', 'previous': 'previous_url'}

    @classmethod
    def students_affectations_uuid_get(*args, **kwargs):
        return StudentAffectationGet(
            student=Student(uuid=str(uuid.uuid4()), last_name='', first_name=''),
            period=PeriodGet(uuid=str(uuid.uuid4()), name='P1'),
            score=ScoreListGet(uuid=str(uuid.uuid4()))
        )

    @classmethod
    def scores_student_uuid_period_uuid_get(*args, **kwargs):
        return ScoreGet(objectives={}, comments={})

    @classmethod
    def scores_student_uuid_period_uuid_put(*args, **kwargs):
        return kwargs.get('score_get')

    @classmethod
    def scores_uuid_get(*args, **kwargs):
        return ScoreGet(uuid=str(uuid.uuid4()), objectives={}, comments={})

    @classmethod
    def students_affectations_specialty_organization_stats_get(*args, **kwargs):
        return {'total_count': 2, 'validated_count': 1}

    @classmethod
    def masters_allocations_post(*args, **kwargs):
        return AllocationGet(uuid=str(uuid.uuid4()), role=ChoiceRole.DELEGATE.name)

    @classmethod
    def masters_allocations_uuid_delete(*args, **kwargs):
        return AllocationGet(uuid=str(uuid.uuid4()), role=ChoiceRole.DELEGATE.name), 200, {}

    @classmethod
    def scores_affectation_uuid_validate_post(*args, **kwargs):
        success_response = None, 204, {}
        error_response = {'error': 'error'}, 404, {}
        return random.choice([success_response, error_response])

    @classmethod
    def scores_uuid_put(*args, **kwargs):
        return {}, 200, {}

    @classmethod
    def masters_allocations_get(*args, **kwargs):
        return {'count': 1, 'results': [AllocationGet(
            uuid=str(uuid.uuid4()),
            organization=OrganizationGet(uuid=str(uuid.uuid4()), reference=''),
            specialty=SpecialtyGet(uuid=str(uuid.uuid4()), acronym=''),
            role=ChoiceRole.MASTER.name,
        )]}

