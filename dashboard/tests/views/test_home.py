##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2018 Université catholique de Louvain (http://www.uclouvain.be)
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
from django.conf import settings
from django.contrib.auth.models import Permission
from django.test import TestCase
from django.urls import reverse

from base.tests.factories.user import UserFactory


class TestHome(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory()
        cls.url = reverse("home")

    def setUp(self):
        self.client.force_login(self.user)

    def test_user_is_not_logged(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertRedirects(response, f"/login/?next={self.url}")

    def test_template_used(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "dashboard.html")

    def test_osis_vpn_help_url(self):
        response = self.client.get(self.url)
        context = response.context
        self.assertEqual(context["osis_vpn_help_url"], settings.OSIS_VPN_HELP_URL)

    def test_user_has_access_to_tutor_dashboard(self):
        self.user.user_permissions.add(Permission.objects.get(codename="is_tutor"))
        response = self.client.get(self.url)
        self.assertEqual(response.context['grids_tiles'][0].tag, 'tutor')

    def test_user_has_access_to_student_dashboard(self):
        self.user.user_permissions.add(Permission.objects.get(codename="is_student"))
        response = self.client.get(self.url)
        self.assertEqual(response.context['grids_tiles'][0].tag, 'student')
