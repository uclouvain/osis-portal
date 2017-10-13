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

from base import models as mdl_base
from base.models.enums import component_type

from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.learning_unit_year import LearningUnitYearFactory
from base.tests.factories.learning_unit_component import LearningUnitComponentFactory


def create_learning_unit_component(data):
    learning_unit_component = mdl_base.learning_unit_component.LearningUnitComponent()
    if 'learning_unit_year' in data:
        learning_unit_component.learning_unit_year = data['learning_unit_year']
    if 'type' in data:
        learning_unit_component.type = data['type']
    if 'duration' in data:
        learning_unit_component.duration = data['duration']
    learning_unit_component.save()
    return learning_unit_component


class LearningUnitComponentTest(TestCase):
    def setUp(self):
        today = datetime.datetime.today()
        self.an_academic_year = AcademicYearFactory(year=today.year)

    def test_search_by_type(self):
        a_learning_unit_year = LearningUnitYearFactory(academic_year=self.an_academic_year)
        lecturing_learning_unit_component = LearningUnitComponentFactory(learning_unit_year=a_learning_unit_year,
                                                                         type=component_type.LECTURING)
        practical_learning_unit_component = LearningUnitComponentFactory(learning_unit_year=a_learning_unit_year,
                                                                         type=component_type.PRACTICAL_EXERCISES)

        self.assertCountEqual(mdl_base.learning_unit_component.search(a_learning_unit_year, component_type.LECTURING),
                         [lecturing_learning_unit_component])

    def test_search(self):
        a_learning_unit_year = LearningUnitYearFactory(academic_year=self.an_academic_year)
        lecturing_learning_unit_component = LearningUnitComponentFactory(learning_unit_year=a_learning_unit_year,
                                                                         type=component_type.LECTURING)
        practical_learning_unit_component = LearningUnitComponentFactory(learning_unit_year=a_learning_unit_year,
                                                                         type=component_type.PRACTICAL_EXERCISES)

        self.assertCountEqual(mdl_base.learning_unit_component.search(a_learning_unit_year, None),
                              [lecturing_learning_unit_component, practical_learning_unit_component])
