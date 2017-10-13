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
from base import models as mdl_base
from base.tests.factories.academic_year import AcademicYearFactory
from django.test import TestCase


now = datetime.datetime.now()


def create_academic_year():
    an_academic_year = mdl_base.academic_year.AcademicYear()
    an_academic_year.year = 2016
    an_academic_year.save()
    return an_academic_year


def create_academic_year_with_year(a_year):
    an_academic_year = mdl_base.academic_year.AcademicYear(year=a_year,
                                                           start_date=datetime.datetime(a_year, now.month, 1),
                                                           end_date=datetime.datetime(a_year+1, now.month, 28))
    an_academic_year.save()
    return an_academic_year


def create_academic_year_current():
    an_academic_year = mdl_base.academic_year.AcademicYear()
    an_academic_year.year = now.year
    an_academic_year.start_date = now
    an_academic_year.end_date = now
    an_academic_year.save()
    return an_academic_year


class AcademicYearTest(TestCase):
    def setUp(self):
        # Create a list with 4 unordered academic_years : Y+1, Y-1, Y, Y+2 (Y = current year)
        self.academic_years = [AcademicYearFactory(year=now.year+x) for x in [1, -1, 0, 2]]
        self.sorted_academic_years = sorted(self.academic_years, key=lambda ay: ay.year)
        self.current_academic_years = [ay for ay in self.sorted_academic_years
                                       if ay.start_date <= now.date() < ay.end_date]

    def test_find_academic_years(self):
        self.assertListEqual(list(mdl_base.academic_year.find_academic_years()), self.sorted_academic_years)

    def test_current_academic_years(self):
        self.assertListEqual(list(mdl_base.academic_year.current_academic_years()), self.current_academic_years)

    def test_current_academic_year(self):
        self.assertEqual(mdl_base.academic_year.current_academic_year(), self.current_academic_years[0])

    def test_starting_academic_year(self):
        self.assertEqual(mdl_base.academic_year.starting_academic_year(), self.current_academic_years[-1])

    def test_find_by_year(self):
        searched_academic_year = self.academic_years[0]
        self.assertEqual(mdl_base.academic_year.find_by_year(searched_academic_year.year), searched_academic_year)

    def test_find_by_inexisting_year(self):
        self.assertIsNone(mdl_base.academic_year.find_by_year(10))
