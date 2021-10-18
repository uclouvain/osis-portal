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
import uuid

import mock
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils.datetime_safe import date
from osis_internship_sdk.model.allocation_get import AllocationGet

from base.models.signals import GROUP_MASTERS_INTERNSHIP
from base.tests.factories.person import PersonFactory
from base.tests.factories.user import UserFactory
from internship.models.enums.role_choice import ChoiceRole
from internship.tests.services.test_api_client import MockAPI


@override_settings(URL_INTERNSHIP_API='url_test_api')
class TestScoreEncoding(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = PersonFactory().user
        cls.api_patcher = mock.patch("internship.services.internship.InternshipAPIClient.__new__", return_value=MockAPI)

    def setUp(self):
        self.client.force_login(self.user)
        self.api_patcher.start()
        self.addCleanup(self.api_patcher.stop)

    def test_access_manage_delegates(self):
        url = reverse('internship_manage_delegates')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'internship_manage_delegates.html')

    @mock.patch('internship.tests.services.test_api_client.MockAPI.masters_uuid_allocations_get')
    def test_delegates_cannot_access_manage_delegates(self, mock_masters_allocations):
        mock_masters_allocations.return_value = {'count': 1, 'results': [
            AllocationGet(uuid=str(uuid.uuid4()), role=ChoiceRole.DELEGATE.name)
        ]}
        url = reverse('internship_manage_delegates')
        response = self.client.get(url)
        self.assertRedirects(response, reverse('internship_master_home'))

    @mock.patch('internship.views.master_delegates._get_internship_reference', return_value='A01')
    def test_create_new_delegate(self, mock_internship_reference):
        url = reverse('internship_new_delegate', kwargs={
            'specialty_uuid': uuid.uuid4(),
            'organization_uuid': uuid.uuid4()
        })
        person = PersonFactory()
        response = self.client.post(url, data={
            'first_name': person.first_name,
            'last_name': person.last_name,
            'birth_date': date.today(),
            'email': person.email,
            'civility': 'DOCTOR'
        })
        self.assertRedirects(response, reverse('internship_manage_delegates')+"?internship={}".format(
            mock_internship_reference.return_value
        ))

    @mock.patch('internship.views.master_delegates._get_internship_reference', return_value='A01')
    def test_should_add_existing_user_to_group_when_delegate_created(self, mock_internship_reference):
        existing_user = UserFactory()
        url = reverse('internship_new_delegate', kwargs={
            'specialty_uuid': uuid.uuid4(),
            'organization_uuid': uuid.uuid4()
        })
        person = PersonFactory()
        response = self.client.post(url, data={
            'first_name': person.first_name,
            'last_name': person.last_name,
            'birth_date': date.today(),
            'email': existing_user.email,
            'civility': 'DOCTOR'
        })
        self.assertRedirects(response, reverse('internship_manage_delegates')+"?internship={}".format(
            mock_internship_reference.return_value
        ))
        self.assertIn(GROUP_MASTERS_INTERNSHIP, existing_user.groups.all().values_list('name', flat=True))

    def test_delete_delegate(self):
        url = reverse('internship_delete_delegate', kwargs={'allocation_uuid': uuid.uuid4()})
        response = self.client.get(url)
        self.assertRedirects(response, reverse('internship_manage_delegates'))
