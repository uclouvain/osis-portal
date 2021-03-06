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
import datetime

import mock
from django.conf import settings
from django.test import TestCase
from django.urls import reverse
from osis_attribution_sdk import ApplicationCourseCalendar

from base.tests.factories.user import UserFactory


class TestHome(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory()
        cls.url = reverse("home")

    def setUp(self):
        self.calendar = ApplicationCourseCalendar(
            title="Candidature aux cours vacants",
            start_date=datetime.datetime.today() - datetime.timedelta(days=10),
            end_date=datetime.datetime.today() + datetime.timedelta(days=15),
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

        self.client.force_login(self.user)

    def test_user_is_not_logged(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertRedirects(response, "/login/?next={}".format(self.url))

    def test_template_used(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "dashboard.html")

    def test_with_online_application_not_opened(self):
        self.calendar.start_date = datetime.datetime.today() + datetime.timedelta(days=5)
        self.calendar.is_open = False

        response = self.client.get(self.url)
        context = response.context
        self.assertFalse(context["online_application_opened"])

    def test_with_online_application_opened(self):
        response = self.client.get(self.url)
        context = response.context
        self.assertTrue(context["online_application_opened"])

    def test_manage_courses_url(self):
        response = self.client.get(self.url)
        context = response.context
        self.assertEqual(context["manage_courses_url"], settings.OSIS_MANAGE_COURSES_URL)

    def test_osis_vpn_help_url(self):
        response = self.client.get(self.url)
        context = response.context
        self.assertEqual(context["osis_vpn_help_url"], settings.OSIS_VPN_HELP_URL)
