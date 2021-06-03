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
import datetime
import uuid

import mock
from django.contrib.auth.models import Permission, User
from django.http import HttpResponseNotAllowed, HttpResponse
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from osis_attribution_sdk.model.application import Application
from osis_attribution_sdk.model.vacant_course import VacantCourse
from osis_attribution_sdk.model.vacant_declaration_type_enum import VacantDeclarationTypeEnum
from osis_attribution_sdk.models import ApplicationCourseCalendar

from attribution.forms.application import VacantAttributionFilterForm
from base.templatetags.academic_year_display import display_as_academic_year
from base.tests.factories.tutor import TutorFactory
from base.tests.factories.user import UserFactory


class OnlineApplicationContextTestMixin:
    calendar = None

    def open_application_course_calendar(self):
        self.calendar = ApplicationCourseCalendar(
            title="Candidature aux cours vacants",
            start_date=datetime.date.today() - datetime.timedelta(days=10),
            end_date=datetime.date.today() + datetime.timedelta(days=15),
            authorized_target_year=2020,
            is_open=True
        )
        self.application_remote_calendar_patcher = mock.patch.multiple(
            'attribution.views.online_application.ApplicationCoursesRemoteCalendar',
            __init__=mock.Mock(return_value=None),
            _calendars=mock.PropertyMock(return_value=[self.calendar])
        )
        self.application_remote_calendar_patcher.start()
        self.addCleanup(self.application_remote_calendar_patcher.stop)

    def add_can_access_application_permission_to_user(self, user: User):
        codename = "can_access_attribution_application"
        perm = Permission.objects.filter(codename=codename).first()
        user.user_permissions.add(perm)


class TestOutsideEncodingPeriodView(OnlineApplicationContextTestMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.url = reverse('outside_applications_period')
        cls.tutor = TutorFactory(person__global_id='578945612')

    def setUp(self) -> None:
        self.open_application_course_calendar()

        self.add_can_access_application_permission_to_user(self.tutor.person.user)
        self.client.force_login(self.tutor.person.user)

    def test_case_period_closed_assert_message_displayed(self):
        self.calendar.start_date = datetime.date.today() + datetime.timedelta(days=5)
        self.calendar.is_open = False

        response = self.client.get(self.url)

        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].tags, 'warning')

        expected_msg = _(
            'The period of online application for courses %(year)s will open on %(start_date)s to %(end_date)s'
        ) % {
           'year': display_as_academic_year(self.calendar.authorized_target_year),
           'start_date': self.calendar.start_date.strftime('%d/%m/%Y'),
           'end_date': self.calendar.end_date.strftime('%d/%m/%Y')
       }
        self.assertEqual(messages[0].message, expected_msg)

    def test_case_period_opened_assert_redirect_to_overview(self):
        expected_redirect = reverse('applications_overview')
        response = self.client.get(self.url, follow=False)

        self.assertRedirects(response, expected_redirect, fetch_redirect_response=False)  # Redirection


class TestApplicationOverviewView(OnlineApplicationContextTestMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.url = reverse('applications_overview')
        cls.tutor = TutorFactory(person__global_id='578945612')

    def setUp(self) -> None:
        self.open_application_course_calendar()
        self.add_can_access_application_permission_to_user(self.tutor.person.user)

        # Mock application service
        self.get_applications_mocked = mock.Mock(return_value=[])
        self.get_attribution_about_to_expires_mocked = mock.Mock(return_value=[])
        self.application_service_patcher = mock.patch.multiple(
            'attribution.views.online_application.ApplicationService',
            get_applications=self.get_applications_mocked,
            get_attribution_about_to_expires=self.get_attribution_about_to_expires_mocked,

        )
        self.application_service_patcher.start()
        self.addCleanup(self.application_service_patcher.stop)

        # Mock attribution service
        self.get_attributions_list = mock.Mock(return_value=[])
        self.attribution_service_patcher = mock.patch.multiple(
            'attribution.views.online_application.AttributionService',
            get_attributions_list=self.get_attributions_list,
        )
        self.attribution_service_patcher.start()
        self.addCleanup(self.attribution_service_patcher.stop)

        self.client.force_login(self.tutor.person.user)

    def test_case_user_not_logged(self):
        self.client.logout()

        response = self.client.get(self.url, follow=False)
        self.assertEqual(response.status_code, 401)

    def test_case_user_without_permission(self):
        self.client.force_login(UserFactory())

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 401)

    def test_case_calendar_not_opened_assert_redirection_to_outside_encoding_period(self):
        self.calendar.start_date = datetime.date.today() + datetime.timedelta(days=5)
        self.calendar.is_open = False

        expected_redirect = reverse('outside_applications_period')
        response = self.client.get(self.url, follow=False)
        self.assertRedirects(response, expected_redirect, fetch_redirect_response=False)  # Redirection

    def test_assert_methods_not_allowed(self):
        methods_not_allowed = ['post']

        for method in methods_not_allowed:
            response = getattr(self.client, method)(self.url)
            self.assertEqual(response.status_code, HttpResponseNotAllowed.status_code)

    @override_settings(ATTRIBUTION_CONFIG={
        "HELP_BUTTON_URL": "https://dummy-url.com",
        "CATALOG_URL": "https://catalogue_url.com"
    })
    def test_get_method_assert_context(self):
        response = self.client.get(self.url, follow=False)

        self.assertEqual(response.status_code, HttpResponse.status_code)
        self.assertEqual(response.context['a_tutor'], self.tutor)
        self.assertEqual(response.context['application_course_calendar'], self.calendar)
        self.assertEqual(
            response.context['application_academic_year'],
            display_as_academic_year(self.calendar.authorized_target_year)
        )
        self.assertEqual(
            response.context['previous_academic_year'],
            display_as_academic_year(self.calendar.authorized_target_year - 1)
        )
        self.assertEqual(response.context['help_button_url'], "https://dummy-url.com")
        self.assertEqual(response.context['catalog_url'], "https://catalogue_url.com")

        self.assertTrue("attributions_about_to_expire" in response.context)
        self.assertTrue("attributions" in response.context)
        self.assertTrue("tot_lecturing" in response.context)
        self.assertTrue("tot_practical" in response.context)
        self.assertTrue("applications" in response.context)

    def test_get_method_called_multiple_service_to_fetch_data(self):
        self.client.get(self.url, follow=False)

        # Application Service
        self.assertTrue(self.get_applications_mocked.called)
        self.assertTrue(self.get_attribution_about_to_expires_mocked.called)

        # Attribution Service
        self.assertTrue(self.get_attributions_list.called)


class TestSearchVacantCourseView(OnlineApplicationContextTestMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.url = reverse('search_vacant_courses')
        cls.tutor = TutorFactory(person__global_id='578945612')

    def setUp(self):
        self.open_application_course_calendar()
        self.add_can_access_application_permission_to_user(self.tutor.person.user)

        # Create mock ApplicationService
        self.search_vacant_courses_mocked = mock.Mock(return_value=[])
        self.application_service_patcher = mock.patch.multiple(
            'attribution.views.online_application.ApplicationService',
            search_vacant_courses=self.search_vacant_courses_mocked
        )
        self.application_service_patcher.start()
        self.addCleanup(self.application_service_patcher.stop)

        self.client.force_login(self.tutor.person.user)

    def test_case_user_not_logged(self):
        self.client.logout()

        response = self.client.get(self.url, follow=False)
        self.assertEqual(response.status_code, 401)

    def test_case_user_without_permission(self):
        self.client.force_login(UserFactory())

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 401)

    def test_case_calendar_not_opened_assert_redirection_to_outside_encoding_period(self):
        self.calendar.start_date = datetime.date.today() + datetime.timedelta(days=5)
        self.calendar.is_open = False

        expected_redirect = reverse('outside_applications_period')
        response = self.client.get(self.url, follow=False)
        self.assertRedirects(response, expected_redirect, fetch_redirect_response=False)  # Redirection

    def test_assert_methods_not_allowed(self):
        methods_not_allowed = ['post']

        for method in methods_not_allowed:
            response = getattr(self.client, method)(self.url)
            self.assertEqual(response.status_code, HttpResponseNotAllowed.status_code)

    @override_settings(ATTRIBUTION_CONFIG={
        "HELP_BUTTON_URL": "https://dummy-url.com"
    })
    def test_get_assert_context(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, HttpResponse.status_code)
        self.assertEqual(response.context['a_tutor'], self.tutor)
        self.assertIsInstance(response.context['form'], VacantAttributionFilterForm)
        self.assertEqual(response.context['help_button_url'], "https://dummy-url.com")

    def test_get_with_queryparams_assert_call_application_service(self):
        query_params = {'learning_container_acronym': 'LDR'}

        response = self.client.get(self.url, data=query_params)
        self.assertEqual(response.status_code, HttpResponse.status_code)

        self.assertTrue(self.search_vacant_courses_mocked.called)


class TestCreateApplicationView(OnlineApplicationContextTestMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.url = reverse('create_application', kwargs={'vacant_course_code': 'LDROI1200'})
        cls.tutor = TutorFactory(person__global_id='578945612')

    def setUp(self):
        # Create event to open calendar + Mock Remove API Call for calendar
        self.open_application_course_calendar()
        self.add_can_access_application_permission_to_user(self.tutor.person.user)

        # Create mock ApplicationService
        self.create_application_mocked = mock.Mock(return_value=None)
        self.get_vacant_course_mocked = mock.Mock(
            return_value=VacantCourse(
                code='LDROI1200',
                year=2020,
                lecturing_volume_total='20.0',
                practical_volume_total='10.0',
                lecturing_volume_available='10.0',
                practical_volume_available='10.0',
                title='Introduction au droit',
                vacant_declaration_type=VacantDeclarationTypeEnum("RESEVED_FOR_INTERNS"),
                vacant_declaration_type_text='Reserved for interns',
                is_in_team=False,
                allocation_entity='DRT',
            )
        )

        self.application_service_patcher = mock.patch.multiple(
            'attribution.views.online_application.ApplicationService',
            create_application=self.create_application_mocked,
            get_vacant_course=self.get_vacant_course_mocked
        )
        self.application_service_patcher.start()
        self.addCleanup(self.application_service_patcher.stop)

        self.client.force_login(self.tutor.person.user)

    def test_case_user_not_logged(self):
        self.client.logout()

        response = self.client.get(self.url, follow=False)
        self.assertEqual(response.status_code, 401)

    def test_case_user_without_permission(self):
        self.client.force_login(UserFactory())

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 401)

    def test_case_calendar_not_opened_assert_redirection_to_outside_encoding_period(self):
        self.calendar.start_date = datetime.date.today() + datetime.timedelta(days=5)
        self.calendar.is_open = False

        expected_redirect = reverse('outside_applications_period')
        response = self.client.get(self.url, follow=False)
        self.assertRedirects(response, expected_redirect, fetch_redirect_response=False)

    @override_settings(ATTRIBUTION_CONFIG={
        "HELP_BUTTON_URL": "https://dummy-url.com"
    })
    def test_get_method_assert_context(self):
        response = self.client.get(self.url, follow=False)

        self.assertEqual(response.status_code, HttpResponse.status_code)
        self.assertEqual(response.context['a_tutor'], self.tutor)
        self.assertEqual(response.context['save_url'], self.url)
        self.assertEqual(response.context['cancel_url'], reverse('applications_overview'))
        self.assertEqual(response.context['help_button_url'], "https://dummy-url.com")

    def test_post_assert_call_application_service(self):
        response = self.client.post(self.url, data={}, follow=False)

        expected_redirect = reverse('applications_overview')
        self.assertRedirects(response, expected_redirect, fetch_redirect_response=False)

        self.assertTrue(self.create_application_mocked.called)


class TestUpdateApplicationView(OnlineApplicationContextTestMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.application_uuid = uuid.uuid4()
        cls.url = reverse('update_application', kwargs={'application_uuid': cls.application_uuid})
        cls.tutor = TutorFactory(person__global_id='578945612')

    def setUp(self):
        self.open_application_course_calendar()
        self.add_can_access_application_permission_to_user(self.tutor.person.user)

        # Create mock ApplicationService
        self.update_application_mocked = mock.Mock(return_value=None)
        self.get_vacant_course_mocked = mock.Mock(
            return_value=VacantCourse(
                code='LDROI1200',
                year=2020,
                lecturing_volume_total='20.0',
                practical_volume_total='10.0',
                lecturing_volume_available='10.0',
                practical_volume_available='10.0',
                title='Introduction au droit',
                vacant_declaration_type=VacantDeclarationTypeEnum("RESEVED_FOR_INTERNS"),
                vacant_declaration_type_text='Reserved for interns',
                is_in_team=False,
                allocation_entity='DRT',
            )
        )
        self.get_application_mocked = mock.Mock(
            return_value=Application(
                uuid=str(self.application_uuid),
                code='LDROI1200',
                year=2020,
                lecturing_volume='10.0',
                practical_volume='5.0',
                remark='',
                course_summary='',
            )
        )

        self.application_service_patcher = mock.patch.multiple(
            'attribution.views.online_application.ApplicationService',
            update_application=self.update_application_mocked,
            get_application=self.get_application_mocked,
            get_vacant_course=self.get_vacant_course_mocked
        )
        self.application_service_patcher.start()
        self.addCleanup(self.application_service_patcher.stop)

        self.client.force_login(self.tutor.person.user)

    def test_case_user_not_logged(self):
        self.client.logout()

        response = self.client.get(self.url, follow=False)
        self.assertEqual(response.status_code, 401)

    def test_case_user_without_permission(self):
        self.client.force_login(UserFactory())

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 401)

    def test_case_calendar_not_opened_assert_redirection_to_outside_encoding_period(self):
        self.calendar.start_date = datetime.date.today() + datetime.timedelta(days=5)
        self.calendar.is_open = False

        expected_redirect = reverse('outside_applications_period')
        response = self.client.get(self.url, follow=False)
        self.assertRedirects(response, expected_redirect, fetch_redirect_response=False)

    @override_settings(ATTRIBUTION_CONFIG={
        "HELP_BUTTON_URL": "https://dummy-url.com"
    })
    def test_get_method_assert_context(self):
        response = self.client.get(self.url, data={}, follow=False)

        self.assertEqual(response.status_code, HttpResponse.status_code)
        self.assertEqual(response.context['a_tutor'], self.tutor)
        self.assertEqual(response.context['save_url'], self.url)
        self.assertEqual(response.context['cancel_url'], reverse('applications_overview'))
        self.assertEqual(response.context['help_button_url'], "https://dummy-url.com")

    def test_post_assert_call_application_service(self):
        response = self.client.post(self.url, data={}, follow=False)

        expected_redirect = reverse('applications_overview')
        self.assertRedirects(response, expected_redirect, fetch_redirect_response=False)

        self.assertTrue(self.update_application_mocked.called)


class TestRenewMultipleAttributionsAboutToExpireView(OnlineApplicationContextTestMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.url = reverse('renew_applications')
        cls.tutor = TutorFactory(person__global_id='578945612')

    def setUp(self):
        self.open_application_course_calendar()
        self.add_can_access_application_permission_to_user(self.tutor.person.user)

        # Create mock ApplicationService
        self.renew_attributions_about_to_expire_mocked = mock.Mock(return_value=[])
        self.application_service_patcher = mock.patch.multiple(
            'attribution.views.online_application.ApplicationService',
            renew_attributions_about_to_expire=self.renew_attributions_about_to_expire_mocked
        )
        self.application_service_patcher.start()
        self.addCleanup(self.application_service_patcher.stop)

        self.client.force_login(self.tutor.person.user)

    def test_case_user_not_logged(self):
        self.client.logout()

        response = self.client.post(self.url, follow=False)
        self.assertEqual(response.status_code, 401)

    def test_case_user_without_permission(self):
        self.client.force_login(UserFactory())

        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 401)

    def test_case_calendar_not_opened_assert_redirection_to_outside_encoding_period(self):
        self.calendar.start_date = datetime.date.today() + datetime.timedelta(days=5)
        self.calendar.is_open = False

        expected_redirect = reverse('outside_applications_period')
        response = self.client.post(self.url, follow=False)
        self.assertRedirects(response, expected_redirect, fetch_redirect_response=False)

    def test_assert_methods_not_allowed(self):
        methods_not_allowed = ['get']

        for method in methods_not_allowed:
            response = getattr(self.client, method)(self.url)
            self.assertEqual(response.status_code, HttpResponseNotAllowed.status_code)

    def test_post_assert_call_application_service(self):
        post_data = {'vacant_course_LDROI1200': 'on'}

        response = self.client.post(self.url, data=post_data, follow=False)

        expected_redirect = reverse('applications_overview')
        self.assertRedirects(response, expected_redirect, fetch_redirect_response=False)

        self.assertTrue(self.renew_attributions_about_to_expire_mocked.called)


class TestDeleteApplicationView(OnlineApplicationContextTestMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.url = reverse('delete_application', kwargs={'application_uuid': uuid.uuid4()})
        cls.tutor = TutorFactory(person__global_id='578945612')

    def setUp(self):
        self.open_application_course_calendar()
        self.add_can_access_application_permission_to_user(self.tutor.person.user)

        # Create mock ApplicationService
        self.delete_application_mocked = mock.Mock(return_value=[])
        self.application_service_patcher = mock.patch.multiple(
            'attribution.views.online_application.ApplicationService',
            delete_application=self.delete_application_mocked
        )
        self.application_service_patcher.start()
        self.addCleanup(self.application_service_patcher.stop)

        self.client.force_login(self.tutor.person.user)

    def test_case_user_not_logged(self):
        self.client.logout()

        response = self.client.post(self.url, follow=False)
        self.assertEqual(response.status_code, 401)

    def test_case_user_without_permission(self):
        self.client.force_login(UserFactory())

        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 401)

    def test_case_calendar_not_opened_assert_redirection_to_outside_encoding_period(self):
        self.calendar.start_date = datetime.date.today() + datetime.timedelta(days=5)
        self.calendar.is_open = False

        expected_redirect = reverse('outside_applications_period')
        response = self.client.post(self.url, follow=False)
        self.assertRedirects(response, expected_redirect, fetch_redirect_response=False)

    def test_assert_methods_not_allowed(self):
        methods_not_allowed = ['get']

        for method in methods_not_allowed:
            response = getattr(self.client, method)(self.url)
            self.assertEqual(response.status_code, HttpResponseNotAllowed.status_code)

    def test_post_assert_call_application_service(self):
        response = self.client.post(self.url, data={}, follow=False)

        expected_redirect = reverse('applications_overview')
        self.assertRedirects(response, expected_redirect, fetch_redirect_response=False)

        self.assertTrue(self.delete_application_mocked.called)

