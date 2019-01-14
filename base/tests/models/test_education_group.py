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

from base.models import education_group
from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.education_group import EducationGroupFactory
from base.tests.factories.education_group_year import EducationGroupYearFactory
from base.tests.factories.offer_enrollment import OfferEnrollmentFactory
from base.tests.factories.student import StudentFactory


class EducationGroupTest(TestCase):
    def setUp(self):
        now = datetime.date.today()
        a_year = now.year
        self.education_group = EducationGroupFactory()
        self.education_group2 = EducationGroupFactory()
        self.education_group3 = EducationGroupFactory()
        self.academic_year = AcademicYearFactory(year=2015)
        self.academic_year2 = AcademicYearFactory(year=2017)
        self.curent_academic_year = AcademicYearFactory(
            year=a_year,
            start_date=datetime.datetime(a_year, now.month, 1),
            end_date=datetime.datetime(a_year + 1, now.month, 28)
        )
        self.education_group_year1 = EducationGroupYearFactory(
            education_group= self.education_group,
            academic_year=self.academic_year
        )
        self.education_group_year2 = EducationGroupYearFactory(
            education_group= self.education_group,
            academic_year=self.academic_year2
        )
        self.education_group_year_current = EducationGroupYearFactory(
            education_group=self.education_group2,
            academic_year=self.curent_academic_year
        )
        self.student = StudentFactory()
        self.OfferEnrollment = OfferEnrollmentFactory(
            student=self.student,
            education_group_year=self.education_group_year_current,
            date_enrollment=now
        )

    def test_most_recent_acronym(self):
        self.assertEqual(self.education_group.most_recent_acronym, self.education_group_year2.acronym)
        self.assertEqual(self.education_group3.most_recent_acronym, None)

    def test_find_by_student(self):
        self.assertCountEqual(education_group.find_by_student(self.student), [self.education_group2])

