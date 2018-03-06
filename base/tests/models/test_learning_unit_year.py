##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2018 Université catholique de Louvain (http://www.uclouvain.be)
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

from base import models as mdl_base
from base.models.enums import learning_unit_year_subtypes
from base.models.learning_container_year import LearningContainerYear
from base.models.learning_unit_year import LearningUnitYear
from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.learning_unit import LearningUnitFactory
from base.tests.factories.learning_unit_year import LearningUnitYearFactory

LAUT5263 = 'LAUT5263'
LDROI1000 = 'LDROI1000'
LDROI2000 = 'LDROI2000'


def create_learning_unit_year(data):
    learning_unit_year = mdl_base.learning_unit_year.LearningUnitYear(**data)
    learning_unit_year.save()
    return learning_unit_year


class LearningUnitYearTest(TestCase):
    def setUp(self):
        today = datetime.datetime.today()
        self.an_academic_year = AcademicYearFactory(year=today.year)

    def test_find_first(self):
        a_learning_unit = LearningUnitFactory()
        a_learning_unit_year_1 = LearningUnitYearFactory(academic_year=self.an_academic_year,
                                                         learning_unit=a_learning_unit,
                                                         acronym=LDROI1000)
        self.assertEqual(mdl_base.learning_unit_year.find_first(self.an_academic_year, a_learning_unit),
                         a_learning_unit_year_1)

    def test_search_order_by_acronym_check_alphabetical_order(self):
        ldroi1000_learning_unit_year = LearningUnitYearFactory(academic_year=self.an_academic_year,
                                                               acronym=LDROI1000)
        laut5263_learning_unit_year = LearningUnitYearFactory(academic_year=self.an_academic_year,
                                                              acronym=LAUT5263)
        self.assertEqual(list(mdl_base.learning_unit_year.search_order_by_acronym(self.an_academic_year)),
                         [laut5263_learning_unit_year, ldroi1000_learning_unit_year])

    def test_search(self):
        a_learning_unit = LearningUnitFactory()
        ldroi1000_learning_unit_year = LearningUnitYearFactory(academic_year=self.an_academic_year,
                                                               learning_unit=a_learning_unit,
                                                               acronym=LDROI1000)
        LearningUnitYearFactory(academic_year=self.an_academic_year, learning_unit=a_learning_unit, acronym=LAUT5263)
        self.assertEqual(list(mdl_base.learning_unit_year.search(self.an_academic_year,
                                                                 LDROI1000,
                                                                 None,
                                                                 a_learning_unit)),
                         [ldroi1000_learning_unit_year])

    def test_find_by_acronym(self):
        ldroi1000_learning_unit_year = LearningUnitYearFactory(academic_year=self.an_academic_year,
                                                               acronym=LDROI1000)
        LearningUnitYearFactory(academic_year=self.an_academic_year, acronym=LAUT5263)
        ldroi2000_learning_unit_year = LearningUnitYearFactory(academic_year=self.an_academic_year,
                                                               acronym=LDROI2000)

        self.assertCountEqual(mdl_base.learning_unit_year.find_by_acronym('LDR', self.an_academic_year),
                              [ldroi1000_learning_unit_year, ldroi2000_learning_unit_year])

    def test_find_first_by_exact_acronym(self):
        a_learning_unit = LearningUnitFactory()
        ldroi1000_learning_unit_year = LearningUnitYearFactory(academic_year=self.an_academic_year,
                                                               learning_unit=a_learning_unit, acronym='LDROI1000')
        ldroi1000_learning_unit_year.save()
        ldroi1000_learning_unit_year_bis = LearningUnitYearFactory(academic_year=self.an_academic_year,
                                                                   learning_unit=a_learning_unit, acronym='LDROI1000')
        ldroi1000_learning_unit_year_bis.save()
        self.assertEqual(mdl_base.learning_unit_year.find_first_by_exact_acronym(self.an_academic_year, 'LDROI1000'),
                         ldroi1000_learning_unit_year)

    def _create_learning_unit_year_partim(self, common_title, speicific_title):
        return LearningUnitYear(
            subtype=learning_unit_year_subtypes.PARTIM,
            specific_title=speicific_title,
            learning_container_year=LearningContainerYear(common_title=common_title)
        )

    def test_complete_title_property_case_common_title_is_none(self):
        specific_title = 'part 1: Vertebrate'
        learn_unit_year = self._create_learning_unit_year_partim(None, specific_title)
        self.assertEqual(learn_unit_year.complete_title, specific_title)
        learn_unit_year = self._create_learning_unit_year_partim('', specific_title)
        self.assertEqual(learn_unit_year.complete_title, specific_title)

    def test_complete_title_property_case_specific_title_is_none(self):
        common_title = 'Zoology'
        learn_unit_year = self._create_learning_unit_year_partim(common_title, None)
        self.assertEqual(learn_unit_year.complete_title, common_title)
        learn_unit_year = self._create_learning_unit_year_partim(common_title, '')
        self.assertEqual(learn_unit_year.complete_title, common_title)

    def test_complete_title_property_case_common_and_specific_title_are_set(self):
        specific_title = 'part 1: Vertebrate'
        common_title = 'Zoology'
        learn_unit_year = self._create_learning_unit_year_partim(common_title, specific_title)
        self.assertEqual(learn_unit_year.complete_title, '{} {}'.format(common_title, specific_title))
