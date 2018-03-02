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

from django.conf import settings
from django.test import TestCase
from django.contrib.auth.models import Group
from django.core.urlresolvers import reverse

from attribution.tests.factories.attribution import AttributionFactory
from base.models.enums import academic_calendar_type
from base.tests.factories.academic_calendar import AcademicCalendarFactory
from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.user import UserFactory


class TestHome(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.client.force_login(self.user)
        self.url = reverse("home")

    def test_user_is_not_logged(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertRedirects(response, "/login/?next={}".format(self.url))

    def test_template_used(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "dashboard.html")

    def test_with_online_application_not_opened(self):
        response = self.client.get(self.url)
        context = response.context
        self.assertFalse(context["online_application_opened"])

    def test_with_online_application_opened(self):
        today = datetime.date.today()
        current_academic_year = AcademicYearFactory(year=today.year, start_date=today-datetime.timedelta(days=5),
                                                    end_date=today+datetime.timedelta(days=5))
        AcademicCalendarFactory(academic_year=current_academic_year,
                                reference=academic_calendar_type.TEACHING_CHARGE_APPLICATION)
        response = self.client.get(self.url)
        context = response.context
        self.assertTrue(context["online_application_opened"])

    def test_with_summary_course_submission_not_opened(self):
        response = self.client.get(self.url)
        context = response.context
        self.assertFalse(context["summary_course_submission_opened"])

    def test_with_summary_course_submission_opened(self):
        today = datetime.date.today()
        current_academic_year = AcademicYearFactory(year=today.year, start_date=today - datetime.timedelta(days=5),
                                                    end_date=today + datetime.timedelta(days=5))
        AcademicCalendarFactory(academic_year=current_academic_year,
                                reference=academic_calendar_type.SUMMARY_COURSE_SUBMISSION)
        response = self.client.get(self.url)
        context = response.context
        self.assertTrue(context["summary_course_submission_opened"])

    def test_is_not_summary_responsible(self):
        Group.objects.create(name="tutors")
        AttributionFactory()

        response = self.client.get(self.url)
        context = response.context
        self.assertFalse(context["is_summary_responsible"])

    def test_is_summary_responsible(self):
        Group.objects.create(name="tutors")
        an_attribution = AttributionFactory(summary_responsible=True)
        an_attribution.tutor.person.user = self.user
        an_attribution.tutor.person.save()

        response = self.client.get(self.url)
        context = response.context
        self.assertTrue(context["is_summary_responsible"])

    def test_manage_courses_url(self):
        response = self.client.get(self.url)
        context = response.context
        self.assertEqual(context["manage_courses_url"], settings.OSIS_MANAGE_COURSES_URL)

    def test_osis_vpn_help_url(self):
        response = self.client.get(self.url)
        context = response.context
        self.assertEqual(context["osis_vpn_help_url"], settings.OSIS_VPN_HELP_URL)
