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
import datetime
import json

from django.contrib.auth.models import Group, Permission
from django.test import TestCase
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from mock import patch

from attestation.views import main as v_main
from attribution.business.xls_students_by_learning_unit import _columns_registration_id_to_text
from base.forms.base_forms import RegistrationIdForm
from base.tests.factories.education_group_year import EducationGroupYearFactory
from base.tests.factories.offer_enrollment import OfferEnrollmentFactory
from base.tests.factories.person import PersonFactory
from base.tests.factories.student import StudentFactory

OK = 200
ACCESS_DENIED = 401

STUDENT_REGISTRATION_ID = "70531800"
STUDENT_GLOBAL_ID = "78961314"


def open_sample_pdf():
    pdf_path = 'attestation/tests/resources/sample.pdf'
    with open(pdf_path) as pdf_file:
        return pdf_file


class HomeTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.url = reverse('attestation_home')
        cls.person = PersonFactory()

        students_group = Group.objects.create(name='students')
        cls.permission = Permission.objects.get(codename="is_student")
        students_group.permissions.add(cls.permission)

    def setUp(self):
        self.client.force_login(self.person.user)

    def test_without_being_logged(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertRedirects(response, '/login/?next={}'.format(self.url))

    def test_with_user_not_a_student(self):
        response = self.client.get(self.url, follow=True)

        self.assertTemplateUsed(response, "access_denied.html")
        self.assertEqual(response.status_code, ACCESS_DENIED)

    def test_with_multiple_students_assigned_same_person(self):
        student1 = StudentFactory(person=self.person)
        student2 = StudentFactory(person=self.person)
        education_group_year = EducationGroupYearFactory()
        OfferEnrollmentFactory(education_group_year=education_group_year, student=student1)
        OfferEnrollmentFactory(education_group_year=education_group_year, student=student2)
        msg = _("A problem was detected with your registration : 2 registration id's are linked to your user. Please "
                "contact the registration departement (SIC). Thank you.")
        response = self.client.get(self.url, follow=True)

        self.assertTemplateUsed(response, "dashboard.html")

        messages = list(response.context['messages'])

        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].tags, 'error')
        self.assertEqual(messages[0].message, msg)

    @patch('attestation.queues.student_attestation_status.fetch_json_attestation_statuses', side_effect=lambda x: None)
    def test_when_not_receive_attestation_statuses(self, mock_fetch_json_attestation_statuses):
        a_student = StudentFactory(person=self.person)
        response = self.client.get(self.url, follow=True)

        self.assertTrue(mock_fetch_json_attestation_statuses.called)
        self.assertEqual(response.status_code, OK)
        self.assertTemplateUsed(response, 'attestation_home_student.html')

        self.assertEqual(response.context['student'], a_student)

        self.assertFalse(response.context['attestations'])
        self.assertFalse(response.context['current_year'])

    @patch('attestation.queues.student_attestation_status.fetch_json_attestation_statuses',
           side_effect=lambda x: {'current_year': 2015, 'attestations': [], 'registration_id': STUDENT_REGISTRATION_ID})
    def test_when_receive_attestation_statuses(self, mock_fetch_json_attestation_statuses):
        a_student = StudentFactory(person=self.person, registration_id=STUDENT_REGISTRATION_ID)
        response = self.client.get(self.url, follow=True)

        self.assertTrue(mock_fetch_json_attestation_statuses.called)
        self.assertEqual(response.status_code, OK)
        self.assertTemplateUsed(response, 'attestation_home_student.html')

        self.assertEqual(response.context['student'], a_student)
        self.assertEqual(response.context['current_year'], 2015)

        self.assertFalse(response.context['attestations'])

    @patch('attestation.queues.student_attestation_status.fetch_json_attestation_statuses',
           side_effect=lambda x: {'current_year': 2015, 'attestations': [], 'registration_id': STUDENT_REGISTRATION_ID})
    def test_when_registration_id_doesnt_match(self, mock_fetch_json_attestation_statuses):
        a_student = StudentFactory(person=self.person)

        with self.assertRaises(Exception) as e:
            self.client.get(self.url, follow=True)

        self.assertTrue(mock_fetch_json_attestation_statuses.called)
        self.assertEqual(str(e.exception), _('Registration fetched doesn\'t match with student registration_id'))

    def test_when_no_student_find_by_user(self):
        self.person.user.user_permissions.add(self.permission)
        response = self.client.get(self.url, follow=True)

        self.assertEqual(response.status_code, OK)
        self.assertTemplateUsed(response, 'attestation_home_student.html')

        self.assertFalse(response.context['attestations'])
        self.assertFalse(response.context['student'])
        self.assertFalse(response.context['current_year'])


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

    def test_without_being_logged(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertRedirects(response, '/login/?next={}'.format(self.url))

    def test_with_user_not_a_student(self):
        response = self.client.get(self.url, follow=True)

        self.assertTemplateUsed(response, "access_denied.html")
        self.assertEqual(response.status_code, ACCESS_DENIED)

    def test_with_multiple_students_assigned_same_person(self):
        student1 = StudentFactory(person=self.person)
        student2 = StudentFactory(person=self.person)
        education_group_year = EducationGroupYearFactory()
        OfferEnrollmentFactory(education_group_year=education_group_year, student=student1)
        OfferEnrollmentFactory(education_group_year=education_group_year, student=student2)
        msg = _("A problem was detected with your registration : 2 registration id's are linked to your user. Please "
                "contact the registration departement (SIC). Thank you.")
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
        self.assertEqual(response['Content-Disposition'], 'attachment; filename="{}.pdf"'.format(self.attestation_type))
        self.assertEqual(response.content.decode(), str(open_sample_pdf()))


class AttestationAdministrationTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.url = reverse('attestation_administration')
        cls.person = PersonFactory()

        cls.permission = Permission.objects.get(codename="is_faculty_administrator")
        cls.person.user.user_permissions.add(cls.permission)

    def setUp(self):
        self.client.force_login(self.person.user)

    def test_without_being_logged(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertRedirects(response, '/login/?next={}'.format(self.url))

    def test_when_user_is_not_a_faculty_administrator(self):
        a_person = PersonFactory()
        self.client.force_login(a_person.user)
        response = self.client.get(self.url, follow=True)

        self.assertTemplateUsed(response, "access_denied.html")
        self.assertEqual(response.status_code, ACCESS_DENIED)

    def test_when_faculty_administrator(self):

        response = self.client.get(self.url, follow=True)

        self.assertEqual(response.status_code, OK)
        self.assertTemplateUsed(response, "admin/attestation_administration.html")


class SelectStudentAttestationTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.url = reverse('attestation_admin_select_student')
        cls.person = PersonFactory()

        cls.permission = Permission.objects.get(codename="is_faculty_administrator")
        cls.person.user.user_permissions.add(cls.permission)

        Group.objects.create(name='students')

    def setUp(self):
        self.client.force_login(self.person.user)

    def test_without_being_logged(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertRedirects(response, '/login/?next={}'.format(self.url))

    def test_when_user_is_not_a_faculty_administrator(self):
        a_person = PersonFactory()
        self.client.force_login(a_person.user)
        response = self.client.get(self.url, follow=True)

        self.assertTemplateUsed(response, "access_denied.html")
        self.assertEqual(response.status_code, ACCESS_DENIED)

    def test_get_request(self):
        response = self.client.get(self.url, follow=True)

        self.assertEqual(response.status_code, OK)
        self.assertTemplateUsed(response, "admin/attestation_administration.html")

        self.assertIsInstance(response.context['form'], RegistrationIdForm)

    def test_invalid_post_request(self):
        response = self.client.post(self.url, data={'registration_id': STUDENT_REGISTRATION_ID}, follow=True)

        self.assertEqual(response.status_code, OK)
        self.assertTemplateUsed(response, "admin/attestation_administration.html")
        # Message valided in base test
        self.assertEqual(len(response.context['form'].errors), 1)

    @patch('attestation.queues.student_attestation_status.fetch_json_attestation_statuses', side_effect=lambda x: None)
    def test_valid_post_request_but_no_attestation(self, mock_fetch_json_attestation_statuses):
        a_student = StudentFactory(registration_id=STUDENT_REGISTRATION_ID)
        response = self.client.post(self.url, data={'registration_id': STUDENT_REGISTRATION_ID}, follow=True)

        self.assertTrue(mock_fetch_json_attestation_statuses.called)

        self.assertEqual(response.status_code, OK)
        self.assertTemplateUsed(response, "attestation_home_admin.html")

        self.assertEqual(response.context['student'], a_student)

        self.assertFalse(response.context['attestations'])
        self.assertFalse(response.context['current_year'])

    @patch('attestation.queues.student_attestation_status.fetch_json_attestation_statuses',
           side_effect=lambda x: {'current_year': 2015, 'attestations': [], 'registration_id' : STUDENT_REGISTRATION_ID})
    def test_valid_post_request(self, mock_fetch_json_attestation_statuses):
        a_student = StudentFactory(registration_id=STUDENT_REGISTRATION_ID)
        response = self.client.post(self.url, data={'registration_id': STUDENT_REGISTRATION_ID}, follow=True)

        self.assertTrue(mock_fetch_json_attestation_statuses.called)

        self.assertEqual(response.status_code, OK)
        self.assertTemplateUsed(response, "attestation_home_admin.html")

        self.assertEqual(response.context['student'], a_student)
        self.assertEqual(response.context['current_year'], 2015)

        self.assertFalse(response.context['attestations'])


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
