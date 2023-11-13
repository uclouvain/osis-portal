##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2023 Université catholique de Louvain (http://www.uclouvain.be)
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

from django.test import TestCase
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from attribution.tests.views.online_application.common import OnlineApplicationContextTestMixin
from base.templatetags.academic_year_display import display_as_academic_year
from base.tests.factories.person import PersonFactory
from base.tests.factories.tutor import TutorFactory


class TestOutsideEncodingPeriodView(OnlineApplicationContextTestMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.url = reverse('outside_applications_period')
        cls.person = PersonFactory(global_id="9999999")

    def setUp(self) -> None:
        self.open_application_course_calendar()
        self.client.force_login(self.person.user)

    def test_case_period_closed_assert_message_displayed(self):
        self.calendar.start_date = datetime.date.today() + datetime.timedelta(days=5)
        self.calendar.is_open = False

        response = self.client.get(self.url)

        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].tags, 'warning')

        expected_msg = _(
            'The period of online application for courses %(year)s will open on %(start_date)s until %(end_date)s'
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
