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
from django.contrib.auth.models import User, AnonymousUser, Permission
from django.test import TestCase, RequestFactory
from attestation.views import main as v_main

class TestHome(TestCase):

    ACCESS_DENIED_STATUS = 403
    OK_STATUS = 200
    LOGIN_REQUIRED_STATUS = 302

    @classmethod
    def setUpTestData(cls):
        cls.anonymous = AnonymousUser()
        cls.student_permission = Permission.objects.get(name='Is student')
        cls.user1 = User.objects.create_user(username='user1', password='password1')
        cls.user2 = User.objects.create_user(username='user2', password='password2')
        cls.user2.user_permissions.add(cls.student_permission)

    def setUp(self):
        self.factory = RequestFactory()
        self.request = self.factory.get('/attestation/')

    def test_not_anonymous(self):
        self.request.user = self.anonymous
        response = v_main.home(self.request)
        self.assertEqual(response.status_code, self.LOGIN_REQUIRED_STATUS)

    def test_not_student(self):
        self.request.user = self.anonymous
        response = v_main.home(self.request)
        self.assertEqual(response.status_code, self.ACCESS_DENIED_STATUS)

    def test_student(self):
        self.request.user = self.user2
        response = v_main.home(self.request)
        self.assertEqual(response.status_code, self.OK_STATUS)