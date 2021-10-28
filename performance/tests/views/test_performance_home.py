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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
import json
from types import SimpleNamespace

import mock
from django.contrib.auth.models import Group, Permission
from django.core.exceptions import MultipleObjectsReturned
from django.http import HttpResponse
from django.test import TestCase
from django.urls import reverse

from base.tests.factories.person import PersonFactory
from base.tests.factories.student import StudentFactory
from performance.models.enums import offer_registration_state
from performance.tests.factories.student_performance import StudentPerformanceFactory
from performance.tests.views.test_main import ACCESS_DENIED, MULTIPLE_STUDENT_ERROR, OK


class ViewPerformanceHomeStudentTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        students_group = Group.objects.create(name="students")
        permission = Permission.objects.get(codename="is_student")
        students_group.permissions.add(permission)

        cls.student = StudentFactory()
        cls.url = reverse('performance_home')

    def setUp(self):
        self.client.force_login(self.student.person.user)
        self.student_performance = StudentPerformanceFactory(
            registration_id=self.student.registration_id,
            academic_year=2021
        )

        # Mock the OSIS Remote API Call
        self.discriminate_user_patcher = mock.patch(
            "base.business.student.find_by_user_and_discriminate",
        )
        self.mocked_discriminate_user = self.discriminate_user_patcher.start()
        self.addCleanup(self.discriminate_user_patcher.stop)

    def test_user_not_logged(self):
        self.client.logout()
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, "/login/?next={}".format(self.url))

    def test_user_not_a_student(self):
        a_person = PersonFactory()
        self.client.logout()
        self.client.force_login(a_person.user)

        response = self.client.get(self.url, follow=True)

        self.assertEqual(response.status_code, ACCESS_DENIED)
        self.assertTemplateUsed(response, 'access_denied.html')

    def test_multiple_students_objects_for_one_user(self):
        self.mocked_discriminate_user.side_effect = MultipleObjectsReturned
        response = self.client.get(self.url)

        self.assertTemplateUsed(response, 'dashboard.html')

        messages = list(response.context['messages'])

        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].tags, 'error')
        self.assertEqual(messages[0].message, MULTIPLE_STUDENT_ERROR)

    def test_assert_context_keys(self):
        self.mocked_discriminate_user.return_value = self.student
        response = self.client.get(self.url)

        self.assertTemplateUsed(response, 'performance_home_student.html')
        self.assertEqual(response.status_code, OK)

        self.assertEqual(response.context['student'], self.student)
        expected_row = {
            'academic_year': self.student_performance.academic_year_template_formated,
            'acronym': self.student_performance.acronym,
            'title': json.loads(
                json.dumps(self.student_performance.data)
            )["monAnnee"]["monOffre"]["offre"]["intituleComplet"],
            'pk': self.student_performance.pk,
            'offer_registration_state': self.student_performance.offer_registration_state
        }
        self.assertEqual(response.context['programs'], [expected_row])
        self.assertEqual(
            response.context['registration_states_to_show'],
            offer_registration_state.STATES_TO_SHOW_ON_PAGE
        )

    def test_assert_template_used(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, HttpResponse.status_code)
        self.assertTemplateUsed(response, 'performance_home_student.html')


class ViewPerformanceHomeAdminTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.person = PersonFactory()
        cls.person.user.user_permissions.add(Permission.objects.get(codename="is_faculty_administrator"))
        students_group = Group.objects.create(name="students")
        permission = Permission.objects.get(codename="is_student")
        students_group.permissions.add(permission)
        cls.student = StudentFactory()

        cls.url = reverse('performance_student_programs_admin', args=[cls.student.registration_id])
        cls.program_acronym = 'FSA1BA'

    def setUp(self):
        self.student_performance = StudentPerformanceFactory(
            registration_id=self.student.registration_id,
            academic_year=2021
        )
        self.client.force_login(self.person.user)
        # Mock the OSIS Remote API Call
        self.offer_enrollment_row = SimpleNamespace(**{
            'acronym': self.program_acronym,
            'year': 2021,
            'title': "Bachelier en sciences de l'ingénieur",
            'pk': 123456,
            'offer_registration_state': offer_registration_state.REGISTERED,
        })

    def test_user_not_logged(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertRedirects(response, "/login/?next={}".format(self.url))

    def test_user_has_not_permission(self):
        self.client.logout()
        patcher = mock.patch('base.views.api.get_managed_programs_as_dict')
        mock_api_call = patcher.start()
        mock_api_call.return_value = {}
        a_person = PersonFactory()
        self.client.force_login(a_person.user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, ACCESS_DENIED)
        self.assertTemplateUsed(response, 'access_denied.html')
        patcher.stop()

    def test_with_no_corresponding_student(self):
        self.student.delete()

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, OK)
        self.assertTemplateUsed(response, 'admin/performance_home_admin.html')

        self.assertIsNone(response.context['student'])
        self.assertEqual(
            response.context['registration_states_to_show'],
            offer_registration_state.STATES_TO_SHOW_ON_PAGE
        )

    def test_when_empty_programs_list(self):
        self.student_performance.delete()
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, OK)
        self.assertTemplateUsed(response, 'admin/performance_home_admin.html')

        self.assertEqual(response.context['student'], self.student)
        self.assertEqual(response.context['programs'], [])
        self.assertEqual(
            response.context['registration_states_to_show'],
            offer_registration_state.STATES_TO_SHOW_ON_PAGE
        )

    def test_when_program(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, OK)
        self.assertTemplateUsed(response, 'admin/performance_home_admin.html')

        self.assertEqual(response.context['student'], self.student)
        expected_row = {
            'academic_year': self.student_performance.academic_year_template_formated,
            'acronym': self.student_performance.acronym,
            'title': json.loads(
                json.dumps(self.student_performance.data)
            )["monAnnee"]["monOffre"]["offre"]["intituleComplet"],
            'pk': self.student_performance.pk,
            'offer_registration_state': self.student_performance.offer_registration_state
        }
        self.assertEqual(response.context['programs'], [expected_row])
        self.assertEqual(
            response.context['registration_states_to_show'],
            offer_registration_state.STATES_TO_SHOW_ON_PAGE
        )

    def test_pgm_manager_ok(self):
        self.client.logout()
        pgm_manager = PersonFactory()
        StudentPerformanceFactory(
            acronym='PHYS1BA',
            registration_id=self.student.registration_id,
            academic_year=2017
        )
        self.client.force_login(pgm_manager.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, OK)
        self.assertTemplateUsed(response, 'admin/performance_home_admin.html')

    def test_pgm_manager_wrong_program(self):
        self.client.logout()
        pgm_manager = PersonFactory()
        new_student = StudentFactory()
        StudentPerformanceFactory(
            acronym="DROI1BA",
            registration_id=new_student.registration_id,
            academic_year=2021
        )
        self.url = reverse('performance_student_programs_admin', args=[new_student.registration_id])
        self.client.force_login(pgm_manager.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, ACCESS_DENIED)
        self.assertTemplateUsed(response, 'access_denied.html')

    def test_user_is_a_student(self):
        self.client.logout()
        self.client.force_login(self.student.person.user)
        response = self.client.get(self.url, follow=True)

        self.assertEqual(response.status_code, ACCESS_DENIED)
        self.assertTemplateUsed(response, 'access_denied.html')
