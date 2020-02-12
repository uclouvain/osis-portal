############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2020 Université catholique de Louvain (http://www.uclouvain.be)
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
############################################################################
from django.test import TestCase

from base.models.learning_container_year import LearningContainerYear
from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.learning_container_year import LearningContainerYearFactory
from base.tests.factories.learning_unit_year import LearningUnitYearFactory


MIN_YEAR_LIMIT = 2015


def fetch_learning_container_year_not_linked_to_learning_unit_year():
    return LearningContainerYear.objects.filter(learningunityear__isnull=True, academic_year__year__gte=MIN_YEAR_LIMIT)


def clean():
    container_year_qs = fetch_learning_container_year_not_linked_to_learning_unit_year()
    for container_year in container_year_qs:
        print("Delete {acronym} ({year})".format(acronym=container_year.acronym, year=container_year.academic_year))
        container_year.delete()


class TestCleanContainerYear(TestCase):
    def setUp(self) -> None:
        academic_year_2018 = AcademicYearFactory(year=2018)
        academic_year_2014 = AcademicYearFactory(year=2014)
        self.empty_container_year_prior_to_2015 = LearningContainerYearFactory(academic_year=academic_year_2014)
        self.empty_container_year = LearningContainerYearFactory(academic_year=academic_year_2018)
        self.container_year_having_luy = LearningContainerYearFactory(
            academic_year=self.empty_container_year.academic_year,
            acronym=self.empty_container_year.acronym
        )
        self.learning_unit_year = LearningUnitYearFactory(learning_container_year=self.container_year_having_luy)

    def test_fetch_learning_container_year_greater_than_2015_not_linked_to_learning_unit_year(self):
        self.assertQuerysetEqual(
            fetch_learning_container_year_not_linked_to_learning_unit_year(),
            [self.empty_container_year],
            transform=lambda obj: obj
        )

    def test_clean_should_suppress_empty_container_year_superior_to_2015(self):
        clean()
        self.assertQuerysetEqual(
            fetch_learning_container_year_not_linked_to_learning_unit_year(),
            []
        )
