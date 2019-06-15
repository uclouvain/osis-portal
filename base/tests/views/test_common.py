##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2018 Université catholique de Louvain (http://www.uclouvain.be)
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
from django.test import TestCase, override_settings
from django.core.urlresolvers import reverse
from django.conf import settings

from base.tests.factories.person import PersonFactory
from base.views.common import common_context_processor


OK = 200
PASSWORD = 'password'


class LoginTest(TestCase):
    def setUp(self):
        self.person = PersonFactory()
        self.person.user.set_password(PASSWORD)
        self.person.user.save()
        self.url = reverse('login')

    @override_settings(OVERRIDED_LOGIN_URL=None)
    def test_get_request(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, OK)
        self.assertTemplateUsed(response, 'registration/login.html')

    @override_settings(OVERRIDED_LOGIN_URL=reverse('logged_out'))
    def test_with_overrided_login_url(self):
        response = self.client.get(self.url)

        self.assertRedirects(response, reverse('logged_out'))

    @override_settings(OVERRIDED_LOGIN_URL=None)
    def test_post_request(self):
        a_user = self.person.user
        data = {'username': a_user.username, 'password': PASSWORD}

        response = self.client.post(self.url, data=data)

        redirect_url = reverse('dashboard_home')
        self.assertRedirects(response, redirect_url)
        self.assertEqual(response.wsgi_request.user, a_user)


class LogOutTest(TestCase):
    @override_settings(OVERRIDED_LOGOUT_URL=None)
    def test_logout(self):
        person = PersonFactory()
        url = reverse('logout')
        self.client.force_login(person.user)

        response = self.client.get(url)

        self.assertFalse(response.wsgi_request.user.is_authenticated())

    @override_settings(OVERRIDED_LOGOUT_URL=reverse('login'))
    def test_with_overrided_logout_url(self):
        person = PersonFactory()
        url = reverse('logout')
        self.client.force_login(person.user)

        response = self.client.get(url)

        self.assertRedirects(response, reverse('login'))


class LoggedOutTest(TestCase):
    def test_request(self):
        url = reverse('logged_out')

        response = self.client.get(url)

        self.assertEqual(response.status_code, OK)
        self.assertTemplateUsed(response, 'logged_out.html')






