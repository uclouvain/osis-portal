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
from datetime import date

from django.test import TestCase, override_settings
from osis_internship_sdk.api.internship_api import InternshipApi
from osis_internship_sdk.model.choice_get import ChoiceGet
from osis_internship_sdk.model.choice_paging import ChoicePaging
from osis_internship_sdk.model.internship_get import InternshipGet
from osis_internship_sdk.model.internship_paging import InternshipPaging
from osis_internship_sdk.model.offer_get import OfferGet
from osis_internship_sdk.model.offer_paging import OfferPaging
from osis_internship_sdk.model.organization_paging import OrganizationPaging
from osis_internship_sdk.model.person import Person
from osis_internship_sdk.model.person_affectation_get import PersonAffectationGet
from osis_internship_sdk.model.place_evaluation_get import PlaceEvaluationGet
from osis_internship_sdk.model.place_evaluation_item_get import PlaceEvaluationItemGet
from osis_internship_sdk.model.score_list_get import ScoreListGet
from osis_internship_sdk.model.student import Student
from osis_internship_sdk.model.student_paging import StudentPaging
from osis_internship_sdk.models import MasterGet, AllocationGet, PeriodGet, SpecialtyGet, OrganizationGet, \
    StudentAffectationGet, CohortGet, ScoreGet

from internship.models.enums.role_choice import ChoiceRole
from internship.services.internship import InternshipAPIClient


class TestAPIClient(TestCase):

    @override_settings(OSIS_INTERNSHIP_SDK_HOST='test_url')
    def test_new_internship_api_client(self):
        api = InternshipAPIClient()
        self.assertEqual(api.api_client.configuration.host, 'test_url')


class MockAPI(InternshipApi):
    @classmethod
    def masters_get(*args, **kwargs):
        return {
            'count': 1, 'results': [MasterGet(uuid=str(uuid.uuid4()), civility="DR", person=Person(last_name="name"))]
        }

    @classmethod
    def masters_post(*args, **kwargs):
        return MasterGet()

    @classmethod
    def masters_uuid_allocations_get(*args, **kwargs):
        parent_specialty = SpecialtyGet(uuid=str(uuid.uuid4()), acronym='PAR', parent=None)
        return {'count': 1, 'results': [AllocationGet(
            uuid=str(uuid.uuid4()),
            organization=OrganizationGet(uuid=str(uuid.uuid4()), reference=''),
            specialty=SpecialtyGet(uuid=str(uuid.uuid4()), acronym='', parent=parent_specialty),
            role=ChoiceRole.MASTER.name,
            master=MasterGet(uuid=str(uuid.uuid4()), civility="DR", person=Person(last_name="name"))
        )]}

    @classmethod
    def periods_get(*args, **kwargs):
        return {'count': 1, 'results': [
            PeriodGet(uuid=str(uuid.uuid4()), name='P1', date_end='2023-01-31', date_start='2023-01-01')
        ]}

    @classmethod
    def specialties_uuid_get(*args, **kwargs):
        return SpecialtyGet(uuid=str(uuid.uuid4()), cohort=CohortGet(uuid=str(uuid.uuid4())), acronym='', parent=None)

    @classmethod
    def organizations_uuid_get(*args, **kwargs):
        return OrganizationGet(
            uuid=str(uuid.uuid4()), reference='', cohort=CohortGet(uuid=str(uuid.uuid4()), name='cohort')
        )

    @classmethod
    def students_affectations_specialty_organization_get(*args, **kwargs):
        affectation = StudentAffectationGet(
            uuid=str(uuid.uuid4()),
            student=Student(uuid=str(uuid.uuid4()), last_name='', first_name=''),
            period=PeriodGet(uuid=str(uuid.uuid4()), name='P1', date_end='2023-01-31', date_start='2023-01-01'),
            score=ScoreListGet(uuid=str(uuid.uuid4()), validated=False),
            internship_uuid=str(uuid.uuid4()),
        )
        return {'count': 1, 'results': [affectation], 'next': 'next_url', 'previous': 'previous_url'}

    @classmethod
    def students_affectations_affectation_uuid_get(*args, **kwargs):
        return StudentAffectationGet(
            student=Student(uuid=str(uuid.uuid4()), last_name='', first_name=''),
            period=PeriodGet(uuid=str(uuid.uuid4()), name='P1', date_end='2023-01-31', date_start='2023-01-01'),
            score=ScoreListGet(uuid=str(uuid.uuid4()), validated=True, comments={}),
            internship_uuid=str(uuid.uuid4()),
        )

    @classmethod
    def scores_student_uuid_period_uuid_get(*args, **kwargs):
        return ScoreGet(objectives={}, comments={})

    @classmethod
    def scores_student_uuid_period_uuid_put(*args, **kwargs):
        return kwargs.get('score_get')

    @classmethod
    def scores_affectation_uuid_get(*args, **kwargs):
        return ScoreGet(uuid=str(uuid.uuid4()), objectives={}, comments={})

    @classmethod
    def students_affectations_specialty_organization_stats_get(*args, **kwargs):
        return {'total_count': 2, 'validated_count': 1}

    @classmethod
    def masters_allocations_post(*args, **kwargs):
        return AllocationGet(
            uuid=str(uuid.uuid4()), role=ChoiceRole.DELEGATE.name,
            master=MasterGet(uuid=str(uuid.uuid4()), civility="DR", person=Person(last_name="name"))
        )

    @classmethod
    def masters_allocations_uuid_delete(*args, **kwargs):
        return AllocationGet(
            uuid=str(uuid.uuid4()), role=ChoiceRole.DELEGATE.name,
            master=MasterGet(uuid=str(uuid.uuid4()), civility="DR", person=Person(last_name="name"))
        ), 200, {}

    @classmethod
    def scores_affectation_uuid_validate_post(*args, **kwargs):
        success_response = None, 204, {}
        error_response = {'error': 'error'}, 404, {}
        return random.choice([success_response, error_response])

    @classmethod
    def scores_affectation_uuid_put(*args, **kwargs):
        return {}, 200, {}

    @classmethod
    def masters_allocations_get(*args, **kwargs):
        return {'count': 1, 'results': [AllocationGet(
            uuid=str(uuid.uuid4()),
            organization=OrganizationGet(uuid=str(uuid.uuid4()), reference=''),
            specialty=SpecialtyGet(uuid=str(uuid.uuid4()), acronym='', parent=None),
            role=ChoiceRole.MASTER.name,
            master=MasterGet(uuid=str(uuid.uuid4()), civility="DR", person=Person(last_name="name"))
        )]}

    @classmethod
    def person_affectations_cohort_person_uuid_get(*args, **kwargs):
        return {'count': 1, 'results': [PersonAffectationGet(
            uuid=str(uuid.uuid4()),
            organization=OrganizationGet(uuid=str(uuid.uuid4()), reference='', name=''),
            speciality=SpecialtyGet(uuid=str(uuid.uuid4()), acronym='', parent=None, name=''),
            period=PeriodGet(uuid=str(uuid.uuid4()), name='P1', date_end='2023-01-31', date_start='2023-01-01'),
            master='',
            internship_evaluated=False,
        )]}

    @classmethod
    def place_evaluation_items_cohort_get(*args, **kwargs):
        return {'count': 1, 'results': [PlaceEvaluationItemGet(
            uuid=str(uuid.uuid4()),
            order=0.0,
            statement='',
            type='',
            options=[],
            required=True,
        )]}

    @classmethod
    def place_evaluation_affectation_uuid_get(*args, **kwargs):
        return PlaceEvaluationGet(evaluation={})

    @classmethod
    def students_get(*args, **kwargs):
        return StudentPaging(count=1.0)

    @classmethod
    def organizations_get(*args, **kwargs):
        return OrganizationPaging(count=1.0, next="", previous="", results=[OrganizationGet(city="Test")])

    @classmethod
    def cohorts_name_get(*args, **kwargs):
        return CohortGet(name="cohort", publication_start_date=str(date.today()))

    @classmethod
    def internships_get(*args, **kwargs):
        return InternshipPaging(count=1.0, next="", previous="", results=[InternshipGet(name="Test")])

    @classmethod
    def choices_get(*args, **kwargs):
        return ChoicePaging(count=1.0, next="", previous="", results=[ChoiceGet(uuid=str(uuid.uuid4()), choice=1)])

    @classmethod
    def offers_get(*args, **kwargs):
        return OfferPaging(count=1.0, next="", previous="", results=[OfferGet(uuid=str(uuid.uuid4()))])

    @classmethod
    def internships_uuid_get(*args, **kwargs):
        return InternshipGet(uuid=str(uuid.uuid4()), name="Test", periods=[], apds=[])
