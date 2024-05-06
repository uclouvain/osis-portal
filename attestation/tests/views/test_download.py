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
import datetime

import mock
from django.contrib.auth.models import Group, Permission
from django.core.exceptions import MultipleObjectsReturned
from django.test import TestCase
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from mock import patch

from attestation.tests.views.test_home import MULTIPLE_STUDENT_ERROR
from base.tests.factories.person import PersonFactory
from base.tests.factories.student import StudentFactory

STUDENT_GLOBAL_ID = "78961314"


def open_sample_pdf():
    pdf_path = 'attestation/tests/resources/sample.pdf'
    with open(pdf_path) as pdf_file:
        return pdf_file


class DownloadAttestationTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        year = datetime.date.today().year
        cls.attestation_type = "test"
        cls.url = reverse('download_attestation', args=[str(year), cls.attestation_type])
        cls.person = PersonFactory()

        students_group = Group.objects.create(name='students')
        cls.permission = Permission.objects.get(codename="is_student")
        students_group.permissions.add(cls.permission)

    def setUp(self):
        self.client.force_login(self.person.user)

        self.discriminate_user_patcher = mock.patch(
            "base.business.student.find_by_user_and_discriminate",
        )
        self.mocked_discriminate_user = self.discriminate_user_patcher.start()
        self.addCleanup(self.discriminate_user_patcher.stop)

    def test_without_being_logged(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertRedirects(response, f'/login/?next={self.url}')

    def test_with_user_not_a_student(self):
        response = self.client.get(self.url, follow=True)
        self.mocked_discriminate_user.return_value = None
        self.assertTemplateUsed(response, "access_denied.html")
        self.assertEqual(response.status_code, 403)

    def test_with_multiple_students_assigned_same_person(self):
        StudentFactory(person=self.person)
        self.mocked_discriminate_user.side_effect = MultipleObjectsReturned
        response = self.client.get(self.url, follow=True)

        self.assertTemplateUsed(response, "dashboard.html")

        messages = list(response.context['messages'])

        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].tags, 'error')
        self.assertEqual(messages[0].message, MULTIPLE_STUDENT_ERROR)

    @patch('attestation.queues.student_attestation.fetch_student_attestation',
           side_effect=lambda global_id, year, attestation_type, username: None)
    def test_when_no_attestation_pdf(self, mock_fetch_student_attestation):
        self.mocked_discriminate_user.return_value = StudentFactory(person=self.person)
        response = self.client.get(self.url, follow=True)

        self.assertTrue(mock_fetch_student_attestation.called)
        self.assertTemplateUsed(response, "attestation_home_student.html")

        messages = list(response.context['messages'])

        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].tags, 'error')
        self.assertEqual(messages[0].message, _('Student attestations'))

    @patch('attestation.queues.student_attestation.fetch_student_attestation',
           side_effect=lambda global_id, year, attestation_type, username: open_sample_pdf())
    def test_when_attestation_pdf_fetched(self, mock_fetch_student_attestation):
        StudentFactory(person=self.person)
        response = self.client.get(self.url, follow=True)

        self.assertTrue(mock_fetch_student_attestation.called)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertEqual(response['Content-Disposition'], f'attachment; filename="{self.attestation_type}.pdf"')
        self.assertEqual(response.content.decode(), str(open_sample_pdf()))


class DownloadStudentAttestation(TestCase):
    @classmethod
    def setUpTestData(cls):
        year = datetime.date.today().year
        cls.attestation_type = "test"
        cls.url = reverse('attestation_admin_download', args=[STUDENT_GLOBAL_ID, year, cls.attestation_type])
        cls.person = PersonFactory()

        cls.permission = Permission.objects.get(codename="is_faculty_administrator")
        cls.person.user.user_permissions.add(cls.permission)

        Group.objects.create(name='students')

    def setUp(self):
        self.client.force_login(self.person.user)

    def test_without_being_logged(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertRedirects(response, f'/login/?next={self.url}')

    def test_when_user_is_not_a_faculty_administrator(self):
        a_person = PersonFactory()
        self.client.force_login(a_person.user)
        response = self.client.get(self.url, follow=True)

        self.assertTemplateUsed(response, "access_denied.html")
        self.assertEqual(response.status_code, 403)

    @patch('attestation.queues.student_attestation.fetch_student_attestation',
           side_effect=lambda global_id, year, attestation_type, username: None)
    def test_when_no_attestation_pdf(self, mock_fetch_student_attestation):
        StudentFactory(person=PersonFactory(global_id=STUDENT_GLOBAL_ID))
        response = self.client.get(self.url, follow=True)

        self.assertTrue(mock_fetch_student_attestation.called)
        self.assertTemplateUsed(response, "attestation_home_admin.html")

        messages = list(response.context['messages'])

        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].tags, 'error')
        self.assertEqual(messages[0].message, _('Student attestations'))

    @patch('attestation.queues.student_attestation.fetch_student_attestation',
           side_effect=lambda global_id, year, attestation_type, username: open_sample_pdf())
    def test_when_attestation_pdf_fetched(self, mock_fetch_student_attestation):
        response = self.client.get(self.url, follow=True)

        self.assertTrue(mock_fetch_student_attestation.called)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertEqual(response['Content-Disposition'], f'attachment; filename="{self.attestation_type}.pdf"')

        self.assertEqual(response.content.decode(), str(open_sample_pdf()))

    @mock.patch("base.business.student.find_by_user_and_discriminate")
    def test_with_multiple_students_assigned_same_person(self, mocked_discriminate_user):
        StudentFactory(person=PersonFactory(global_id=STUDENT_GLOBAL_ID))
        mocked_discriminate_user.side_effect = MultipleObjectsReturned
        response = self.client.get(self.url, follow=True)

        self.assertTemplateUsed(response, "dashboard.html")

        messages = list(response.context['messages'])

        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].tags, 'error')
        self.assertEqual(messages[0].message, MULTIPLE_STUDENT_ERROR)
