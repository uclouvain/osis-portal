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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
from django.contrib.auth.models import Permission
from django.test import TestCase
from django.urls import reverse

from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.person import PersonFactory
from base.tests.factories.tutor import TutorFactory


class TestSelectTutorForAttribution(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.url = reverse("attribution_admin_select_tutor")
        cls.person = PersonFactory()
        permission = Permission.objects.get(codename="is_faculty_administrator")
        cls.person.user.user_permissions.add(permission)

    def setUp(self):
        self.client.force_login(self.person.user)

    def test_is_not_faculty_admin(self):
        self.client.force_login(PersonFactory().user)
        response = self.client.get(self.url, follow=True)

        self.assertEqual(response.status_code, 401)
        self.assertTemplateUsed(response, 'access_denied.html')

    def test_is_faculty_manager(self):
        response = self.client.get(self.url, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/attribution_administration.html')

    def test_select_tutor_for_attribution(self):
        AcademicYearFactory(current=True)
        tutor = TutorFactory()
        response = self.client.post(self.url, data={'global_id': tutor.person.global_id})
        self.assertEqual(response.status_code, 302)
        expected_url = reverse('tutor_charge_admin', kwargs={'global_id': tutor.person.global_id})
        self.assertRedirects(response, expected_url)
