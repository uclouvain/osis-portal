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
import datetime
from django.test import TestCase
from attribution.utils import permission
from base.tests.models import test_academic_year, test_academic_calendar
from django.contrib.auth.models import User


now = datetime.datetime.now()

CURRENT_YEAR = now.year
NEXT_YEAR = now.year + 1


class TestPermission(TestCase):

    def setUp(self):
        self.a_user = User.objects.create_user(username='legat', email='legat@localhost', password='top_secret')

    def test_permission_is_undefined_no_academic_year(self):
        self.assertEqual(permission.is_online_application_opened(self.a_user), False)

    def test_permission_is_undefined_no_academic_calendar(self):
        test_academic_year.create_academic_year_with_year(CURRENT_YEAR)
        test_academic_year.create_academic_year_with_year(NEXT_YEAR)
        self.assertEqual(permission.is_online_application_opened(self.a_user), False)

    def test_application_session_period_opened(self):
        test_academic_year.create_academic_year_with_year(CURRENT_YEAR)
        next_academic_year = test_academic_year.create_academic_year_with_year(NEXT_YEAR)

        test_academic_calendar.create_academic_calendar(next_academic_year,
                                                        permission.TEACHING_CHARGE_APPLICATION,
                                                        now,
                                                        now)

        self.assertEqual(permission.is_online_application_opened(self.a_user), True)

    def test_application_session_period_closed(self):
        test_academic_year.create_academic_year_with_year(CURRENT_YEAR)
        next_academic_year = test_academic_year.create_academic_year_with_year(NEXT_YEAR)
        two_weeks_ago = datetime.datetime.now() - datetime.timedelta(15)
        test_academic_calendar.create_academic_calendar(next_academic_year, permission.TEACHING_CHARGE_APPLICATION,
                                                        datetime.datetime(two_weeks_ago.year,
                                                                          two_weeks_ago.month,
                                                                          two_weeks_ago.day),
                                                        datetime.datetime(two_weeks_ago.year,
                                                                          two_weeks_ago.month,
                                                                          two_weeks_ago.day+1))
        self.assertEqual(permission.is_online_application_opened(self.a_user), False)

