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
from internship.tests.factories.cohort import CohortFactory


class TestCohort(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.cohort = CohortFactory(subscription_start_date=datetime.date(2018, 1, 26),
                                   subscription_end_date=datetime.date(2018, 2, 7),
                                   publication_start_date=datetime.date(2018, 4, 7))


    def test_cohort_enrollments_active(self):
        self.assertTrue(self.cohort.enrollment_active(datetime.date(2018, 1, 26)))
        self.assertTrue(self.cohort.enrollment_active(datetime.date(2018, 2, 7)))

    def test_cohort_enrollments_inactive(self):
        self.assertFalse(self.cohort.enrollment_active(datetime.date(2018, 1, 25)))
        self.assertFalse(self.cohort.enrollment_active(datetime.date(2018, 2, 8)))

    def test_cohort_publication_active(self):
        self.assertTrue(self.cohort.publication_active(datetime.date(2018, 4, 7)))

    def test_cohort_publication_inactive(self):
        self.assertFalse(self.cohort.publication_active(datetime.date(2018, 4, 6)))
