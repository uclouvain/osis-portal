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
import json

from django.conf import settings
from django.contrib.auth.models import Group, Permission
from django.test import TestCase, override_settings
from django.urls import reverse
from mock import patch

from base.tests.factories.person import PersonFactory
from base.tests.factories.student import StudentFactory
from base.tests.factories.user import UserFactory
from base.views import common
from base.views.common import common_context_processor
from osis_common.tests.factories.application_notice import ApplicationNoticeFactory

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

        self.assertFalse(response.wsgi_request.user.is_authenticated)

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


class TestManagedPrograms(TestCase):

    def setUp(self):
        self.person = PersonFactory()
        self.url = reverse('dashboard_home')
        students_group = Group.objects.create(name="students")
        permission = Permission.objects.get(codename="is_student")
        students_group.permissions.add(permission)

    # 1. Preconditions : user is authenticated, user is not a student

    def test_student(self):
        student = StudentFactory(person=self.person)
        self.client.force_login(student.person.user)
        response = self.client.get(self.url)
        context = {'dummy': 'dummy'}
        common._set_managed_programs(response.wsgi_request, context)
        self.assertFalse(context.get('is_faculty_manager', None))
        self.assertTrue(context.get('dummy', None) == 'dummy')

    def test_not_authenticated(self):
        self.client.logout()
        response = self.client.get(self.url)
        context = {'dummy': 'dummy'}
        common._set_managed_programs(response.wsgi_request, context)
        self.assertTrue(len(context) == 1)
        self.assertIsNone(context.get('is_faculty_manager', None))
        self.assertTrue(context.get('dummy', None) == 'dummy')

    def test_get_program_managed_as_dict(self):
        managed_programs = common.get_managed_program_as_dict(self.person.user)
        expected_managed_programs = {
            '2017': ['PHYS1BA', 'BIOL1BA'],
            '2018': ['PHYS1BA', 'BIOL1BA']
        }
        self.assertDictEqual(expected_managed_programs, managed_programs)

    # 2.1. If session key 'is_faculty_manager' is defined :
    # Context 'is_faculty_manager' is updated with value of Session 'is_faculty_manager'
    def test_already_defined(self):
        # Test is True
        self.client.force_login(self.person.user)
        session = self.client.session
        session['is_faculty_manager'] = True
        session.save()
        response = self.client.get(self.url)
        context = {'dummy': 'dummy'}
        common._set_managed_programs(response.wsgi_request, context)
        self.assertTrue(context.get('is_faculty_manager'))
        self.assertTrue(context.get('dummy', None) == 'dummy')
        # Test is False
        session['is_faculty_manager'] = False
        session.save()
        response = self.client.get(self.url)
        context = {'dummy': 'dummy'}
        common._set_managed_programs(response.wsgi_request, context)
        self.assertFalse(context.get('is_faculty_manager'))
        self.assertTrue(context.get('dummy', None) == 'dummy')

    # 2.2.1: If session key 'is_faculty_manager' is not defined
    # The managed programs are retrieved from osis with call to the api
    # 2.2.2: If the managed programs exists :
    # 2.2.2.1: Context 'is_faculty_manager' value is set to True
    # 2.2.2.2: Session 'is_faculty_manager'  value is set to True
    # 2.2.2.1: Session 'managed_programs' value is set with the results of the api call
    def test_not_defined_and_exists(self):
        self.client.force_login(self.person.user)
        response = self.client.get(self.url)
        context = {'dummy': 'dummy'}
        common._set_managed_programs(response.wsgi_request, context)
        expected_managed_programs = {
            '2017': ['PHYS1BA', 'BIOL1BA'],
            '2018': ['PHYS1BA', 'BIOL1BA']
        }
        managed_programs = json.loads(self.client.session.get('managed_programs'))
        self.assertDictEqual(expected_managed_programs, managed_programs)
        self.assertTrue(context.get('is_faculty_manager'))
        self.assertTrue(self.client.session.get('is_faculty_manager'))

    # 2.2.1: If session key 'is_faculty_manager' is not defined
    # The managed programs are retrieved from osis with call to the api
    # 2.2.3: If the managed programs not exists :
    # 2.2.3.1: Context 'is_faculty_manager' value is set to False
    # 2.2.3.2: Session 'is_faculty_manager'  value is set to False
    # 2.2.3.3: Session 'managed_programs' value is set to None
    def test_not_defined_and_not_exists(self):
        patcher = patch('base.views.api.get_managed_programs_as_dict')
        mock_api_call = patcher.start()
        mock_api_call.return_value = {}
        self.client.force_login(self.person.user)
        response = self.client.get(self.url)
        context = {'dummy': 'dummy'}
        common._set_managed_programs(response.wsgi_request, context)
        self.assertIsNone(self.client.session.get('managed_programs'))
        self.assertFalse(context.get('is_faculty_manager'))
        self.assertFalse(self.client.session.get('is_faculty_manager'))
        patcher.stop()


class NoticeTestCase(TestCase):

    def setUp(self):
        self.user = UserFactory()
        self.url = reverse('dashboard_home')
        self.client.force_login(self.user)
        self.response = self.client.get(self.url)
        self.request = self.response.wsgi_request
        self.session = self.client.session
        self.notice = ApplicationNoticeFactory()

    def test_notice_not_session(self):
        context = {'dummy': 'dummy'}
        common._check_notice(self.request, context)
        self.assertEqual(context.get('subject'), self.notice.subject)
        self.assertEqual(context.get('notice'), self.notice.notice)

    def test_notice_in_session(self):
        self.session['subject'] = self.notice.subject
        self.session['notice'] = self.notice.notice
        self.session.save()
        self.response = self.client.get(self.url)
        context = {'dummy': 'dummy'}
        common._check_notice(self.request, context)
        self.assertEqual(self.session.get('subject'), self.notice.subject)
        self.assertEqual(self.session.get('notice'), self.notice.notice)
        self.assertEqual(context.get('subject'), self.notice.subject)
        self.assertEqual(context.get('notice'), self.notice.notice)


class CommonContextProcessorTest(TestCase):

    def setUp(self):
        self.user = UserFactory()
        self.url = reverse('dashboard_home')
        self.client.force_login(self.user)
        self.response = self.client.get(self.url)
        self.request = self.response.wsgi_request

    @override_settings(ENVIRONMENT='env')
    def test_with_defined_environment(self):
        return_value = common_context_processor(self.request)
        expected = {
            'environment': 'env',
            'installed_apps': settings.INSTALLED_APPS,
            'debug': settings.DEBUG,
            'logout_button': settings.LOGOUT_BUTTON,
            'is_faculty_manager': False

        }
        self.assertDictEqual(return_value, expected)

    @override_settings()
    def test_with_no_defined_environment(self):
        del settings.ENVIRONMENT
        return_value = common_context_processor(self.request)
        expected = {
            'environment': 'DEV',
            'installed_apps': settings.INSTALLED_APPS,
            'debug': settings.DEBUG,
            'logout_button': settings.LOGOUT_BUTTON,
            'is_faculty_manager': False
        }
        self.assertDictEqual(return_value, expected)




