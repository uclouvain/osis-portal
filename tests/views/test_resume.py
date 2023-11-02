##############################################################################
#
# OSIS stands for Open Student Information System. It's an application
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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
import uuid
from collections import namedtuple
from unittest import skip

import mock
from django.contrib.auth.models import Permission
from django.test import TestCase
from django.urls import reverse
from osis_internship_sdk.model.allocation_get import AllocationGet
from osis_internship_sdk.model.master_get import MasterGet
from osis_internship_sdk.model.person import Person

from base.tests.factories.student import StudentFactory
from internship.models.enums.civility import Civility
from internship.tests.services.test_api_client import MockAPI
from internship.views.resume import _get_internship_masters_repr


class TestResumeUrl(TestCase):

    def setUp(self):
        self.api_patcher = mock.patch(
            "internship.services.internship.InternshipAPIClient.__new__",
            return_value=MockAPI
        )
        self.client.force_login(self.user)
        self.api_patcher.start()
        self.addCleanup(self.api_patcher.stop)

    @classmethod
    def setUpTestData(cls):
        cls.student = StudentFactory()
        cls.user = cls.student.person.user
        perm = Permission.objects.get(codename="can_access_internship", content_type__model='internshipoffer')
        cls.user.user_permissions.add(perm)

    @skip
    def test_can_access_student_resume(self):
        url = reverse("student_resume", kwargs={'cohort_id': "cohort"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    @mock.patch('internship.services.internship.InternshipAPIService.get_mastered_allocations')
    def test_get_internship_masters_repr(self, mock_mastered_allocations):
        mock_mastered_allocations.return_value = [
            AllocationGet(master=MasterGet(civility=Civility.PROFESSOR.name, person=Person(last_name='TEST')))
        ]

        StudentAffectation = namedtuple('StudentAffectation', ['speciality', 'organization'])
        UuidObj = namedtuple('Object', ['uuid'])

        affectation = StudentAffectation(speciality=UuidObj(uuid=uuid.uuid4()), organization=UuidObj(uuid=uuid.uuid4()))
        repr = _get_internship_masters_repr(self.user.person, affectation)
        self.assertEqual(repr, "Prof. TEST")
