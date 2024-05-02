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
from types import SimpleNamespace

import mock
from django.contrib.auth.models import Permission
from django.test import TestCase, SimpleTestCase
from django.urls import reverse
from osis_attribution_sdk.model.attribution import Attribution
from osis_attribution_sdk.model.attribution_function_enum import AttributionFunctionEnum
from osis_attribution_sdk.model.attribution_links import AttributionLinks
from osis_attribution_sdk.model.learning_unit_type_enum import LearningUnitTypeEnum
from osis_learning_unit_sdk.model.learning_unit import LearningUnit

from attribution.views import tutor_charge
from base.models.enums.learning_container_type import COURSE, OTHER_COLLECTIVE
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
        self.attribution_row = Attribution(**{
            'code': 'LDROI1200',
            'title_fr': 'Introduction aux droits Partie I',
            'title_en': 'Introduction to Law Part I',
            'year': self.current_academic_year.year,
            'type': LearningUnitTypeEnum(value=COURSE),
            'type_text': 'Cours',
            'credits': '15.50',
            'total_learning_unit_charge': '55.5',
            'percentage_allocation_charge': '100%',
            'start_year': 2020,
            'function': AttributionFunctionEnum(value='COORDINATOR'),
            'function_text': 'Coordinateur',
            'lecturing_charge': '15.5',
            'practical_charge': '40.0',
            'links': AttributionLinks(catalog="", schedule=""),
            'is_partim': False,
            'effective_class_repartition': []
        })

        self.learning_unit_row = LearningUnit(**{
            'acronym': 'LDROI1200',
            'has_classes': True
        })

        self.attributions_list_patcher = mock.patch(
            "attribution.services.attribution.AttributionService.get_attributions_list",
            return_value=[self.attribution_row]
        )
        self.learning_units_list_patcher = mock.patch(
            "learning_unit.services.learning_unit.LearningUnitService.get_learning_units",
            return_value=[self.learning_unit_row]
        )
        self.mocked_attributions_list = self.attributions_list_patcher.start()
        self.mocked_learning_units_list = self.learning_units_list_patcher.start()

        self.addCleanup(self.attributions_list_patcher.stop)
        self.addCleanup(self.learning_units_list_patcher.stop)

    def test_case_user_not_logged(self):
        self.client.logout()

        response = self.client.get(self.url)
        self.assertRedirects(response, f'/login/?next={self.url}')

    def test_case_user_have_not_permission(self):
        self.client.force_login(UserFactory())
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, "access_denied.html")

    def test_assert_template_used(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "tutor_charge.html")

    def test_assert_context_keys(self):
        response = self.client.get(self.url)

        self.assertIn("display_years_tab", response.context)
        self.assertEqual(response.context["person"], self.person)
        self.assertEqual(response.context["current_year_displayed"], self.current_academic_year.year)
        self.assertEqual(len(response.context["attributions"]), 1)
        self.assertEqual(response.context["total_lecturing_charge"], 15.5)
        self.assertEqual(response.context["total_practical_charge"], 40.0)

    def test_should_show_volumes(self):
        response = self.client.get(self.url)
        attr = response.context["attributions"][0]
        self.assertTrue(all([attr.lecturing_charge, attr.practical_charge, attr.percentage_allocation_charge]))

    def test_should_hide_volumes_for_learning_unit_other_than_course_and_internship_and_dissertation(self):
        other_attribution = self.attribution_row
        other_attribution.type = LearningUnitTypeEnum(OTHER_COLLECTIVE)

        self.mocked_attributions_list.return_value = [other_attribution]

        response = self.client.get(self.url)
        attr = response.context["attributions"][0]

        self.assertTrue(not any([attr.lecturing_charge, attr.practical_charge, attr.percentage_allocation_charge]))

    def test_should_map_attributions_with_learning_units_to_assess_has_classes(self):
        response = self.client.get(self.url)
        attr = response.context["attributions"][0]

        self.assertEqual(attr.has_classes, self.learning_unit_row.has_classes)


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

        self.learning_unit_row = LearningUnit(**{
            'acronym': 'LDROI1200',
            'has_classes': True
        })

        self.attributions_list_patcher = mock.patch(
            "attribution.views.tutor_charge.TutorChargeView.attributions",
            new_callable=mock.PropertyMock,
            return_value=[self.attribution_row]
        )
        self.mocked_attributions_list = self.attributions_list_patcher.start()
        self.addCleanup(self.attributions_list_patcher.stop)

        self.learning_units_list_patcher = mock.patch(
            "learning_unit.services.learning_unit.LearningUnitService.get_learning_units",
            return_value=[self.learning_unit_row]
        )
        self.mocked_learning_units_list = self.learning_units_list_patcher.start()
        self.addCleanup(self.learning_units_list_patcher.stop)

    def test_case_user_not_logged(self):
        self.client.logout()

        response = self.client.get(self.url)
        self.assertRedirects(response, f'/login/?next={self.url}')

    def test_case_user_have_not_permission(self):
        self.client.force_login(self.tutor.person.user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, "access_denied.html")

    def test_assert_template_used(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "tutor_charge_admin.html")

    def test_assert_context_keys(self):
        response = self.client.get(self.url)

        self.assertIn("display_years_tab", response.context)
        self.assertEqual(response.context["person"], self.tutor.person)
        self.assertEqual(response.context["current_year_displayed"], self.current_academic_year.year)
        self.assertEqual(len(response.context["attributions"]), 1)
        self.assertEqual(response.context["total_lecturing_charge"], 15.5)
        self.assertEqual(response.context["total_practical_charge"], 40.0)
