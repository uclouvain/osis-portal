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
from django.contrib.auth.models import User, Permission
from osis_attribution_sdk.model.application_course_calendar import ApplicationCourseCalendar


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
            'attribution.calendar.application_courses_calendar.ApplicationCoursesRemoteCalendar',
            __init__=mock.Mock(return_value=None),
            _calendars=mock.PropertyMock(return_value=[self.calendar])
        )
        self.application_remote_calendar_patcher.start()
        self.addCleanup(self.application_remote_calendar_patcher.stop)

    @staticmethod
    def add_can_access_application_permission_to_user(user: User):
        codename = "can_access_attribution_application"
        perm = Permission.objects.filter(codename=codename).first()
        user.user_permissions.add(perm)
