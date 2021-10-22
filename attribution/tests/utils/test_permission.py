##############################################################################
#
# OSIS stands for Open Student Information System. It's an application
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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
import mock
from django.test import TestCase

from attribution.calendar.application_courses_calendar import ApplicationCoursesRemoteCalendar
from attribution.utils import permission
from base.tests.factories.person import PersonFactory
from base.tests.factories.user import UserFactory


class TestIsOnlineApplicationOpened(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.a_user = UserFactory()
        cls.a_person = PersonFactory(user=cls.a_user)

    @mock.patch.object(ApplicationCoursesRemoteCalendar, '__init__', return_value=None)
    @mock.patch.object(ApplicationCoursesRemoteCalendar, 'get_target_years_opened', return_value=[])
    def test_is_online_application_opened_case_closed_on_remote_server(self, *mock_obj):
        self.assertFalse(
            permission.is_online_application_opened(self.a_user)
        )

    @mock.patch.object(ApplicationCoursesRemoteCalendar, '__init__', return_value=None)
    @mock.patch.object(ApplicationCoursesRemoteCalendar, 'get_target_years_opened', return_value=[2020])
    def test_is_online_application_opened_case_opened_on_remote_server(self, *mock_obj):
        self.assertTrue(
            permission.is_online_application_opened(self.a_user)
        )
