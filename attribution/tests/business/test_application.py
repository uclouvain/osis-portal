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
from django.test import TestCase
from osis_attribution_sdk import ApplicationCourseCalendar
from django.utils.translation import ugettext_lazy as _

from attribution.business import tutor_application
from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.person import PersonFactory


class ApplicationSendSummaryMail(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.academic_year = AcademicYearFactory(current=True)
        cls.person = PersonFactory()

    def setUp(self):
        self.calendar = ApplicationCourseCalendar(
            title="Candidature aux cours vacants",
            start_date=datetime.datetime.today() - datetime.timedelta(days=10),
            end_date=datetime.datetime.today() + datetime.timedelta(days=15),
            authorized_target_year=self.academic_year.year,
            is_open=True
        )

        self.application_remote_calendar_patcher = mock.patch.multiple(
            'attribution.views.online_application.ApplicationCoursesRemoteCalendar',
            __init__=mock.Mock(return_value=None),
            _calendars=mock.PropertyMock(return_value=[self.calendar])
        )
        self.application_remote_calendar_patcher.start()
        self.addCleanup(self.application_remote_calendar_patcher.stop)

    def test_send_mail_applications_summary_case_no_opened_calendar(self):
        self.calendar.is_open = False

        self.assertEqual(
            tutor_application.send_mail_applications_summary(self.person.global_id),
            _('The period of online application is closed')
        )

    def test_send_mail_applications_summary_case_no_applications(self):
        tutor_application.send_mail_applications_summary(self.person.global_id)

        self.assertEqual(
            tutor_application.send_mail_applications_summary(self.person.global_id),
            _('No application found')
        )
