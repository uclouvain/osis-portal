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
from copy import copy
from functools import partial
from types import SimpleNamespace

import mock
from django.contrib.auth.models import Permission
from django.http import HttpResponse
from django.test import TestCase, SimpleTestCase
from django.urls import reverse
from rest_framework import status

from attribution.views import tutor_charge
from base.models.enums import learning_container_type
from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.person import PersonFactory
from base.tests.factories.tutor import TutorFactory
from base.tests.factories.user import UserFactory


class TutorChargeGetEmailStudentsTest(SimpleTestCase):
    def test_format_students_email_before_new_year_management(self):
        email_expected = "{0}{1}{2}".format(tutor_charge.MAIL_TO, 'ldroi1200', tutor_charge.STUDENT_LIST_EMAIL_END)

        self.assertEqual(
            tutor_charge.get_email_students('LDROI1200', tutor_charge.YEAR_NEW_MANAGEMENT_OF_EMAIL_LIST - 1),
            email_expected
        )

    def test_format_students_email_case_new_management(self):
        email_expected = "{0}{1}-{2}{3}".format(
            tutor_charge.MAIL_TO,
            'lagro1100',
            tutor_charge.YEAR_NEW_MANAGEMENT_OF_EMAIL_LIST,
            tutor_charge.STUDENT_LIST_EMAIL_END
        )

        self.assertEqual(
            tutor_charge.get_email_students('LAGRO1100', tutor_charge.YEAR_NEW_MANAGEMENT_OF_EMAIL_LIST),
            email_expected
        )

    def test_format_students_email_without_acronym(self):
        self.assertIsNone(tutor_charge.get_email_students(None, 2017))


class TutorChargeViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.person = PersonFactory()
        perm = Permission.objects.get(codename="can_access_attribution")
        cls.person.user.user_permissions.add(perm)

        cls.current_academic_year = AcademicYearFactory(current=True)
        cls.url = reverse('tutor_charge')

    def setUp(self) -> None:
        self.client.force_login(self.person.user)

        # Mock the OSIS Remote API Call
        self.attribution_row = SimpleNamespace(**{
            'code': 'LDROI1200',
            'title_fr': 'Introduction aux droits Partie I',
            'title_en': 'Introduction to Law Part I',
            'year': self.current_academic_year.year,
            'type': learning_container_type.COURSE,
            'type_text': 'Cours',
            'credits': '15.50',
            'total_learning_unit_charge': '55.5',
            'percentage_allocation_charge': '100%',
            'start_year': 2020,
            'function': 'COORDINATOR',
            'function_text': 'Coordinateur',
            'lecturing_charge': '15.5',
            'practical_charge': '40.0',
            'links': {},
            'is_partim': False,
            'effective_class_repartition': []
        })
        self.attribution_row.to_dict = partial(vars, self.attribution_row)

        self.attributions_list_patcher = mock.patch(
            "attribution.services.attribution.AttributionService.get_attributions_list",
            return_value=[self.attribution_row]
        )
        self.mocked_attributions_list = self.attributions_list_patcher.start()
        self.addCleanup(self.attributions_list_patcher.stop)

    def test_case_user_not_logged(self):
        self.client.logout()

        response = self.client.get(self.url)
        self.assertRedirects(response, '/login/?next={}'.format(self.url))

    def test_case_user_have_not_permission(self):
        self.client.force_login(UserFactory())
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertTemplateUsed(response, "access_denied.html")

    def test_assert_template_used(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, HttpResponse.status_code)
        self.assertTemplateUsed(response, "tutor_charge.html")

    def test_assert_context_keys(self):
        response = self.client.get(self.url)

        self.assertTrue("display_years_tab" in response.context)
        self.assertEqual(response.context["person"], self.person)
        self.assertEqual(response.context["current_year_displayed"], self.current_academic_year.year)
        self.assertEqual(len(response.context["attributions"]), 1)
        self.assertEqual(response.context["total_lecturing_charge"], 15.5)
        self.assertEqual(response.context["total_practical_charge"], 40.0)

    def test_should_hide_volumes_for_learning_unit_other_than_course_and_internship_and_dissertation(self):
        other_attribution = copy(self.attribution_row)
        other_attribution.type = learning_container_type.OTHER_COLLECTIVE
        other_attribution.to_dict = partial(vars, other_attribution)

        self.mocked_attributions_list.return_value = [other_attribution]

        response = self.client.get(self.url)
        attr = response.context["attributions"][0]

        self.assertTrue(not any([attr.lecturing_charge, attr.practical_charge, attr.percentage_allocation_charge]))


class AdminTutorChargeViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin_person = PersonFactory()
        perm = Permission.objects.get(codename="is_faculty_administrator")
        cls.admin_person.user.user_permissions.add(perm)

        cls.current_academic_year = AcademicYearFactory(current=True)
        cls.tutor = TutorFactory()
        cls.url = reverse('tutor_charge_admin', kwargs={'global_id': cls.tutor.person.global_id})

    def setUp(self) -> None:
        self.client.force_login(self.admin_person.user)

        # Mock the OSIS Remote API Call
        self.attribution_row = SimpleNamespace(**{
            'code': 'LDROI1200',
            'title_fr': 'Introduction aux droits Partie I',
            'title_en': 'Introduction to Law Part I',
            'year': self.current_academic_year.year,
            'type': 'COURSE',
            'type_text': 'Cours',
            'credits': '15.50',
            'total_learning_unit_charge': '55.5',
            'start_year': 2020,
            'function': 'COORDINATOR',
            'function_text': 'Coordinateur',
            'lecturing_charge': '15.5',
            'practical_charge': '40.0',
            'links': {},
            'is_partim': False
        })

        self.attributions_list_patcher = mock.patch(
            "attribution.views.tutor_charge.TutorChargeView.attributions",
            new_callable=mock.PropertyMock,
            return_value=[self.attribution_row]
        )
        self.mocked_attributions_list = self.attributions_list_patcher.start()
        self.addCleanup(self.attributions_list_patcher.stop)

    def test_case_user_not_logged(self):
        self.client.logout()

        response = self.client.get(self.url)
        self.assertRedirects(response, '/login/?next={}'.format(self.url))

    def test_case_user_have_not_permission(self):
        self.client.force_login(self.tutor.person.user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertTemplateUsed(response, "access_denied.html")

    def test_assert_template_used(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, HttpResponse.status_code)
        self.assertTemplateUsed(response, "tutor_charge_admin.html")

    def test_assert_context_keys(self):
        response = self.client.get(self.url)

        self.assertTrue("display_years_tab" in response.context)
        self.assertEqual(response.context["person"], self.tutor.person)
        self.assertEqual(response.context["current_year_displayed"], self.current_academic_year.year)
        self.assertEqual(len(response.context["attributions"]), 1)
        self.assertEqual(response.context["total_lecturing_charge"], 15.5)
        self.assertEqual(response.context["total_practical_charge"], 40.0)
