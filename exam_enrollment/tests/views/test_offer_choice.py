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
from django.contrib.auth.models import User, Permission
from django.test import TestCase
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from base.tests.factories.person import PersonFactory
from base.tests.models import test_academic_year, test_student, test_person
from exam_enrollment.tests.views.test_enrollment_form import _create_group
from performance.models.enums import offer_registration_state


class OfferChoiceTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        group = _create_group('students')
        group.permissions.add(Permission.objects.get(codename='is_student'))
        cls.user = User.objects.create_user(username='jsmith', email='jsmith@localhost', password='secret')
        cls.user.groups.add(group)
        cls.person = test_person.create_person_with_user(cls.user, first_name="James", last_name="Smith")
        cls.student = test_student.create_student_with_registration_person("12345678", cls.person)
        cls.url = reverse("exam_enrollment_offer_choice")

    def setUp(self):
        self.client.force_login(self.user)

        self.offer_enrollment_row = SimpleNamespace(**{
            'acronym': "FSA1BA",
            'year': 2021,
            'title': "Bachelier en sciences de l'ingénieur",
            'pk': 123456,
            'offer_registration_state': offer_registration_state.REGISTERED,
            'student_registration_id': self.student.registration_id
        })
        self.enrollments_list_patcher = mock.patch(
            "exam_enrollment.views.offer_choice.OfferChoice.offer_enrollments_list",
            new_callable=mock.PropertyMock,
            return_value=[self.offer_enrollment_row]
        )
        self.mocked_attributions_list = self.enrollments_list_patcher.start()
        self.addCleanup(self.enrollments_list_patcher.stop)

    def test_user_not_logged(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertRedirects(response, f"/login/?next={self.url}")

    def test_user_has_not_permission(self):
        self.client.logout()
        a_person = PersonFactory()
        self.client.force_login(a_person.user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, 'access_denied.html')

    def test_choose_offer_no_offer_redirect_to_dashboard(self):
        current_academic_year = test_academic_year.create_academic_year_current()
        self.mocked_attributions_list.return_value = []
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, reverse('dashboard_home'))
        messages = list(response.context['messages'])

        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].tags, 'warning')
        self.assertEqual(messages[0].message, _('no_offer_enrollment_found').format(current_academic_year))

    def test_assert_context_keys(self):
        response = self.client.get(self.url)

        self.assertTemplateUsed(response, 'offer_choice.html')
        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.context['student'], self.student)
        self.assertEqual(response.context['programs'], [self.offer_enrollment_row])
