#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2022 Université catholique de Louvain (http://www.uclouvain.be)
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
import datetime

import factory
from osis_assessments_sdk.model.attendance_mark_calendar import AttendanceMarkCalendar

from assessments.services.assessments import AttendanceMarkRemoteCalendar
from base.models.person import Person


class AttendanceMarkSession1CalendarFactory(factory.Factory):
    class Meta:
        model = AttendanceMarkCalendar
        abstract = False

    title = "Demande de note de présence - Session 1"
    start_date = factory.LazyAttribute(lambda o: datetime.date(o.authorized_target_year, 12, 23))
    end_date = factory.LazyAttribute(lambda o: datetime.date(o.authorized_target_year + 1, 2, 28))
    authorized_target_year = 2021
    month_session_name = "Janvier"
    is_open = False


class AttendanceMarkSession2CalendarFactory(AttendanceMarkSession1CalendarFactory):
    class Meta:
        model = AttendanceMarkCalendar
        abstract = False

    title = "Demande de note de présence - Session 2"
    start_date = factory.LazyAttribute(lambda o: datetime.date(o.authorized_target_year + 1, 6, 20))
    end_date = factory.LazyAttribute(lambda o: datetime.date(o.authorized_target_year + 1, 7, 10))
    month_session_name = "Juin"
    is_open = False


class AttendanceMarkSession3CalendarFactory(AttendanceMarkSession1CalendarFactory):
    class Meta:
        model = AttendanceMarkCalendar
        abstract = False

    title = "Demande de note de présence - Session 3"
    start_date = factory.LazyAttribute(lambda o: datetime.date(o.authorized_target_year + 1, 8, 5))
    end_date = factory.LazyAttribute(lambda o: datetime.date(o.authorized_target_year + 1, 9, 15))
    month_session_name = "Septembre"
    is_open = False


class InMemoryAttendanceMarkRemoteCalendar(AttendanceMarkRemoteCalendar):
    def __init__(self, person: Person):
        self._calendars = []
