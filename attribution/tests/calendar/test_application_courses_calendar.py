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
import datetime

import mock
from django.test import SimpleTestCase
from osis_attribution_sdk.models import ApplicationCourseCalendar

from attribution.calendar.application_courses_calendar import ApplicationCoursesRemoteCalendar


class ApplicationCoursesRemoteCalendarTestCase(SimpleTestCase):
    def setUp(self):
        self.event_closed = ApplicationCourseCalendar(
            title="Candidature aux cours vacants [2020]",
            start_date=datetime.date.today() - datetime.timedelta(days=360),
            end_date=datetime.date.today() - datetime.timedelta(days=350),
            authorized_target_year=2020,
            is_open=False
        )

        self.event_opened = ApplicationCourseCalendar(
            title="Candidature aux cours vacants [2021]",
            start_date=datetime.date.today() - datetime.timedelta(days=10),
            end_date=datetime.date.today() + datetime.timedelta(days=15),
            authorized_target_year=2021,
            is_open=True
        )

        self.api_call_patcher = mock.patch(
            'attribution.calendar.application_courses_calendar.'
            'application_api.ApplicationApi.applicationcoursescalendars_list',
            new_callable=mock.PropertyMock,
            create=True,
            return_value=lambda *args, **kwargs: [self.event_closed, self.event_opened]
        )
        self.api_call_mocked = self.api_call_patcher.start()
        self.addCleanup(self.api_call_patcher.stop)

    def test__init__assert_call_remote_api(self):
        calendar = ApplicationCoursesRemoteCalendar()

        self.assertTrue(self.api_call_mocked.called)

    def test_get_target_years_opened(self):
        calendar = ApplicationCoursesRemoteCalendar()

        self.assertListEqual(
            calendar.get_target_years_opened(),
            [self.event_opened.authorized_target_year]
        )

    def test_get_opened_academic_events(self):
        calendar = ApplicationCoursesRemoteCalendar()

        self.assertListEqual(
            calendar.get_opened_academic_events(),
            [self.event_opened]
        )
