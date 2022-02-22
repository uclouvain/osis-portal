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
import mock
from django.http import HttpResponse, HttpResponseForbidden
from django.test import TestCase
from django.urls import reverse

from base.tests.factories.person import PersonFactory
from base.tests.factories.student import StudentFactory


class SelectOfferTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.student = StudentFactory()
        cls.url = reverse("attendance-mark-select-offer")

    def setUp(self):
        self.client.force_login(self.student.person.user)

        self.is_period_opened_patcher = mock.patch(
            "assessments.business.attendance_mark.permission.is_attendance_mark_period_opened",
        )
        self.mocked_is_period_opened = self.is_period_opened_patcher.start()
        self.mocked_is_period_opened.return_value = True
        self.addCleanup(self.is_period_opened_patcher.stop)

    def test_non_student_should_have_permission_denied(self):
        non_student = PersonFactory()
        self.client.force_login(non_student.user)

        response = self.client.get(self.url)
        self.assertEqual(
            response.status_code,
            HttpResponseForbidden.status_code
        )

    def test_should_be_redirected_to_outside_period_page_when_outside_of_attendance_mark_period(self):
        self.mocked_is_period_opened.return_value = False

        response = self.client.get(self.url)

        self.assertRedirects(
            response,
            reverse('outside-attendance-marks-period'),
            fetch_redirect_response=False
        )

    def test_student_should_access_page_when_during_attendance_mark_period(self):
        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            HttpResponse.status_code
        )
        self.assertTemplateUsed(
            response,
            "assessments/attendance_mark/select_offer.html"
        )
