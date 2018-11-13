##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
import json
import datetime
from mock import patch

from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import Group, Permission
from django.core.urlresolvers import reverse
from django.test import TestCase, Client

from base.tests.factories.person import PersonFactory
from base.tests.factories.student import StudentFactory
from base.forms.base_forms import RegistrationIdForm
from attestation.views import main as v_main


OK = 200
BAD_REQUEST = 400
ACCESS_DENIED = 401
FILE_NOT_FOUND = 404
METHOD_NOT_ALLOWED = 405

STUDENT_REGISTRATION_ID = "45451000"
STUDENT_GLOBAL_ID = "78961314"


def open_sample_pdf():
    pdf_path = 'attestation/tests/resources/sample.pdf'
    with open(pdf_path) as pdf_file:
        return pdf_file


class HomeTest(TestCase):
    def setUp(self):
        self.url = reverse('attestation_home')
        self.person = PersonFactory()

        students_group = Group.objects.create(name='students')
        self.permission = Permission.objects.get(codename="is_student")
        students_group.permissions.add(self.permission)

    def test_without_being_logged(self):
        response = self.client.get(self.url)
        self.assertRedirects(response, '/login/?next={}'.format(self.url))

    def test_with_user_not_a_student(self):
        self.client.force_login(self.person.user)
        response = self.client.get(self.url, follow=True)

        self.assertTemplateUsed(response, "access_denied.html")
        self.assertEqual(response.status_code, ACCESS_DENIED)

    def test_with_multiple_students_assigned_same_person(self):
        StudentFactory(person=self.person)
        StudentFactory(person=self.person)
        msg = _("A problem was detected with your registration : 2 registration id's are linked to your user. Please "
                "contact the registration departement (SIC). Thank you.")

        self.client.force_login(self.person.user)
        response = self.client.get(self.url, follow=True)

        self.assertTemplateUsed(response, "dashboard.html")

        messages = list(response.context['messages'])

        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].tags, 'error')
        self.assertEqual(messages[0].message, msg)

    @patch('attestation.queues.student_attestation_status.fetch_json_attestation_statuses', side_effect=lambda x: None)
    def test_when_not_receive_attestation_statuses(self, mock_fetch_json_attestation_statuses):
        a_student = StudentFactory(person=self.person)

        self.client.force_login(self.person.user)
        response = self.client.get(self.url, follow=True)

        self.assertTrue(mock_fetch_json_attestation_statuses.called)
        self.assertEqual(response.status_code, OK)
        self.assertTemplateUsed(response, 'attestation_home_student.html')

        self.assertEqual(response.context['student'], a_student)

        self.assertFalse(response.context['attestation_statuses'])
        self.assertFalse(response.context['academic_year'])
        self.assertFalse(response.context['formated_academic_year'])
        self.assertFalse(response.context['available'])

    @patch('attestation.queues.student_attestation_status.fetch_json_attestation_statuses',
           side_effect=lambda x: {'academicYear': 2015, 'available': False, 'attestationStatuses': []})
    def test_when_receive_attestation_statuses(self, mock_fetch_json_attestation_statuses):
        a_student = StudentFactory(person=self.person)

        self.client.force_login(self.person.user)
        response = self.client.get(self.url, follow=True)

        self.assertTrue(mock_fetch_json_attestation_statuses.called)
        self.assertEqual(response.status_code, OK)
        self.assertTemplateUsed(response, 'attestation_home_student.html')

        self.assertEqual(response.context['student'], a_student)
        self.assertEqual(response.context['academic_year'], 2015)
        self.assertEqual(response.context['formated_academic_year'], "2015 - 2016")

        self.assertFalse(response.context['attestation_statuses'])
        self.assertFalse(response.context['available'])

    def test_when_no_student_find_by_user(self):
        self.person.user.user_permissions.add(self.permission)

        self.client.force_login(self.person.user)
        response = self.client.get(self.url, follow=True)

        self.assertEqual(response.status_code, OK)
        self.assertTemplateUsed(response, 'attestation_home_student.html')

        self.assertFalse(response.context['attestation_statuses'])
        self.assertFalse(response.context['student'])
        self.assertFalse(response.context['academic_year'])
        self.assertFalse(response.context['formated_academic_year'])
        self.assertFalse(response.context['available'])


class DownloadAttestationTest(TestCase):
    def setUp(self):
        year = datetime.date.today().year
        self.attestation_type = "test"
        self.url = reverse('download_attestation', args=[str(year), self.attestation_type])
        self.person = PersonFactory()

        students_group = Group.objects.create(name='students')
        self.permission = Permission.objects.get(codename="is_student")
        students_group.permissions.add(self.permission)

    def test_without_being_logged(self):
        response = self.client.get(self.url)
        self.assertRedirects(response, '/login/?next={}'.format(self.url))

    def test_with_user_not_a_student(self):
        self.client.force_login(self.person.user)
        response = self.client.get(self.url, follow=True)

        self.assertTemplateUsed(response, "access_denied.html")
        self.assertEqual(response.status_code, ACCESS_DENIED)

    def test_with_multiple_students_assigned_same_person(self):
        StudentFactory(person=self.person)
        StudentFactory(person=self.person)
        msg = _("A problem was detected with your registration : 2 registration id's are linked to your user. Please "
                "contact the registration departement (SIC). Thank you.")

        self.client.force_login(self.person.user)
        response = self.client.get(self.url, follow=True)

        self.assertTemplateUsed(response, "dashboard.html")

        messages = list(response.context['messages'])

        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].tags, 'error')
        self.assertEqual(messages[0].message, msg)

    @patch('attestation.queues.student_attestation.fetch_student_attestation',
           side_effect=lambda global_id, year, attestation_type, username: None)
    def test_when_no_attestation_pdf(self, mock_fetch_student_attestation):
        StudentFactory(person=self.person)

        self.client.force_login(self.person.user)
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

        self.client.force_login(self.person.user)
        response = self.client.get(self.url, follow=True)

        self.assertTrue(mock_fetch_student_attestation.called)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertEqual(response['Content-Disposition'], 'attachment; filename="{}.pdf"'.format(self.attestation_type))
        self.assertEqual(response.content.decode(), str(open_sample_pdf()))


class AttestationAdministrationTest(TestCase):
    def setUp(self):
        self.url = reverse('attestation_administration')
        self.person = PersonFactory()

        self.permission = Permission.objects.get(codename="is_faculty_administrator")
        self.person.user.user_permissions.add(self.permission)

    def test_without_being_logged(self):
        response = self.client.get(self.url)
        self.assertRedirects(response, '/login/?next={}'.format(self.url))

    def test_when_user_is_not_a_faculty_administrator(self):
        a_person = PersonFactory()
        self.client.force_login(a_person.user)
        response = self.client.get(self.url, follow=True)

        self.assertTemplateUsed(response, "access_denied.html")
        self.assertEqual(response.status_code, ACCESS_DENIED)

    def test_when_faculty_administrator(self):
        self.client.force_login(self.person.user)

        response = self.client.get(self.url, follow=True)

        self.assertEqual(response.status_code, OK)
        self.assertTemplateUsed(response, "admin/attestation_administration.html")


class SelectStudentAttestationTest(TestCase):
    def setUp(self):
        self.url = reverse('attestation_admin_select_student')
        self.person = PersonFactory()

        self.permission = Permission.objects.get(codename="is_faculty_administrator")
        self.person.user.user_permissions.add(self.permission)

        Group.objects.create(name='students')

    def test_without_being_logged(self):
        response = self.client.get(self.url)
        self.assertRedirects(response, '/login/?next={}'.format(self.url))

    def test_when_user_is_not_a_faculty_administrator(self):
        a_person = PersonFactory()
        self.client.force_login(a_person.user)
        response = self.client.get(self.url, follow=True)

        self.assertTemplateUsed(response, "access_denied.html")
        self.assertEqual(response.status_code, ACCESS_DENIED)

    def test_get_request(self):
        self.client.force_login(self.person.user)

        response = self.client.get(self.url, follow=True)

        self.assertEqual(response.status_code, OK)
        self.assertTemplateUsed(response, "admin/attestation_administration.html")

        self.assertIsInstance(response.context['form'], RegistrationIdForm)

    def test_invalid_post_request(self):
        self.client.force_login(self.person.user)
        msg = _("A problem was detected with your registration : 2 registration id's are linked to your user. Please "
                "contact the registration departement (SIC). Thank you.")

        response = self.client.post(self.url, data={'registration_id': STUDENT_REGISTRATION_ID}, follow=True)

        self.assertEqual(response.status_code, OK)
        self.assertTemplateUsed(response, "admin/attestation_administration.html")

        self.assertFormError(response, 'form', 'registration_id', msg)

    @patch('attestation.queues.student_attestation_status.fetch_json_attestation_statuses', side_effect=lambda x: None)
    def test_valid_post_request_but_no_attestation(self, mock_fetch_json_attestation_statuses):
        a_student = StudentFactory(registration_id=STUDENT_REGISTRATION_ID)
        self.client.force_login(self.person.user)

        response = self.client.post(self.url, data={'registration_id': STUDENT_REGISTRATION_ID}, follow=True)

        self.assertTrue(mock_fetch_json_attestation_statuses.called)

        self.assertEqual(response.status_code, OK)
        self.assertTemplateUsed(response, "attestation_home_admin.html")

        self.assertEqual(response.context['student'], a_student)

        self.assertFalse(response.context['attestation_statuses'])
        self.assertFalse(response.context['academic_year'])
        self.assertFalse(response.context['formated_academic_year'])
        self.assertFalse(response.context['available'])

    @patch('attestation.queues.student_attestation_status.fetch_json_attestation_statuses',
           side_effect=lambda x: {'academicYear': 2015, 'available': False, 'attestationStatuses': []})
    def test_valid_post_request(self, mock_fetch_json_attestation_statuses):
        a_student = StudentFactory(registration_id=STUDENT_REGISTRATION_ID)
        self.client.force_login(self.person.user)

        response = self.client.post(self.url, data={'registration_id': STUDENT_REGISTRATION_ID}, follow=True)

        self.assertTrue(mock_fetch_json_attestation_statuses.called)

        self.assertEqual(response.status_code, OK)
        self.assertTemplateUsed(response, "attestation_home_admin.html")

        self.assertEqual(response.context['student'], a_student)
        self.assertEqual(response.context['academic_year'], 2015)
        self.assertEqual(response.context['formated_academic_year'], "2015 - 2016")

        self.assertFalse(response.context['attestation_statuses'])
        self.assertFalse(response.context['available'])


class DownloadStudentAttestation(TestCase):
    def setUp(self):
        year = datetime.date.today().year
        self.attestation_type = "test"
        self.url = reverse('attestation_admin_download', args=[STUDENT_GLOBAL_ID, year, self.attestation_type])
        self.person = PersonFactory()

        self.permission = Permission.objects.get(codename="is_faculty_administrator")
        self.person.user.user_permissions.add(self.permission)

        Group.objects.create(name='students')

    def test_without_being_logged(self):
        response = self.client.get(self.url)
        self.assertRedirects(response, '/login/?next={}'.format(self.url))

    def test_when_user_is_not_a_faculty_administrator(self):
        a_person = PersonFactory()
        self.client.force_login(a_person.user)
        response = self.client.get(self.url, follow=True)

        self.assertTemplateUsed(response, "access_denied.html")
        self.assertEqual(response.status_code, ACCESS_DENIED)

    @patch('attestation.queues.student_attestation.fetch_student_attestation',
           side_effect=lambda global_id, year, attestation_type, username: None)
    def test_when_no_attestation_pdf(self, mock_fetch_student_attestation):
        StudentFactory(person=PersonFactory(global_id=STUDENT_GLOBAL_ID))
        self.client.force_login(self.person.user)
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
        self.client.force_login(self.person.user)
        response = self.client.get(self.url, follow=True)

        self.assertTrue(mock_fetch_student_attestation.called)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertEqual(response['Content-Disposition'], 'attachment; filename="{}.pdf"'.format(self.attestation_type))
        self.assertEqual(response.content.decode(), str(open_sample_pdf()))


class TestRegistrationIdMessage(TestCase):

    def test_generate_message_with_registration_id(self):
        given_json_message = v_main._make_registration_json_message('1111111')
        expected_json_message = json.loads('{"registration_id" : "1111111"}')
        self.assertJSONEqual(given_json_message, expected_json_message)

    def test_generate_message_without_registration_id(self):
        given_json_message = v_main._make_registration_json_message(None)
        self.assertIsNone(given_json_message)

