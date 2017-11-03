##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2017 Université catholique de Louvain (http://www.uclouvain.be)
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
from decimal import Decimal

from django.contrib.auth.models import Group
from django.test import TestCase

from attribution.business import attribution
from attribution.tests.factories.attribution import AttributionNewFactory
from base.models.academic_year import AcademicYear
from base.models.enums import learning_component_year_type
from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.learning_component_year import LearningComponentYearFactory
from base.tests.factories.learning_container_year import LearningContainerYearFactory
from base.tests.factories.person import PersonFactory
from base.tests.factories.tutor import TutorFactory


class ApplicationTest(TestCase):
    def setUp(self):
        # Creation Person/Tutor
        Group.objects.create(name="tutors")
        self.person = PersonFactory(global_id="98363454")
        TutorFactory(person=self.person)

        _create_multiple_academic_year()
        self.academic_year = AcademicYear.objects.get(year=2017)

        # Creation Json which will be store on attribution
        attributions = _get_attributions_dict()
        AttributionNewFactory(global_id=self.person.global_id,
                              attributions=attributions)

    def test_get_attribution_list(self):
        attribution_list = attribution.get_attribution_list(self.person.global_id,
                                                            self.academic_year)
        self.assertEqual(len(attribution_list), 2)

        academic_year_2016 = AcademicYear.objects.get(year=2016)
        attribution_list = attribution.get_attribution_list(self.person.global_id,
                                                            academic_year_2016)
        self.assertEqual(len(attribution_list), 1)

    def test_get_attribution_list_empty(self):
        academic_year = AcademicYearFactory(year=1990)
        attribution_list = attribution.get_attribution_list(self.person.global_id, academic_year)
        self.assertFalse(attribution_list)

    def test_get_attribution_order(self):
        attribution_list = attribution.get_attribution_list(self.person.global_id,
                                                            self.academic_year)
        self.assertEqual(len(attribution_list), 2)
        self.assertEqual(attribution_list[0]['acronym'], "LBIR1200")
        self.assertEqual(attribution_list[1]['acronym'], "LBIR1300")

    def test_computes_volumes_total(self):
        attribution_list = attribution.get_attribution_list(self.person.global_id,
                                                            self.academic_year)
        volumes_total = attribution.get_volumes_total(attribution_list)
        self.assertTrue(volumes_total)
        self.assertEqual(volumes_total.get(learning_component_year_type.LECTURING), Decimal(33))
        self.assertEqual(volumes_total.get(learning_component_year_type.PRACTICAL_EXERCISES), Decimal(16.5))

    def test_append_team_and_volume_delcared_vacant(self):
        #Create Container Year and component
        _create_learning_container_with_components(acronym="LBIR1300", academic_year=self.academic_year,
                                                   volume_lecturing=Decimal(15.5),
                                                   volume_practical_exercices=Decimal(5))
        _create_learning_container_with_components(acronym="LBIR1200", academic_year=self.academic_year,
                                                   volume_lecturing=Decimal(30),
                                                   volume_practical_exercices=Decimal(75))
        attribution_list = attribution.get_attribution_list(self.person.global_id,
                                                            self.academic_year)
        self.assertEqual(attribution_list[0]['acronym'], "LBIR1200")
        self.assertEqual(attribution_list[0]['volume_lecturing_vacant'], Decimal(30))
        self.assertEqual(attribution_list[0]['volume_practical_exercices_vacant'], Decimal(75))
        self.assertEqual(attribution_list[0]['team'], True)
        self.assertEqual(attribution_list[1]['acronym'], "LBIR1300")
        self.assertEqual(attribution_list[1]['volume_lecturing_vacant'], Decimal(15.5))
        self.assertEqual(attribution_list[1]['volume_practical_exercices_vacant'], Decimal(5))
        self.assertEqual(attribution_list[1]['team'], True)

    def test_append_start_end_academic_year(self):
        attribution_list = attribution.get_attribution_list(self.person.global_id,
                                                            self.academic_year)
        self.assertEqual(attribution_list[0]['acronym'], "LBIR1200")
        self.assertTrue(attribution_list[0]['start_academic_year'])
        self.assertEqual(attribution_list[0]['start_academic_year'].year, 2013)
        self.assertRaises(KeyError, lambda: attribution_list[0]['end_academic_year']) # No end year

        self.assertEqual(attribution_list[1]['acronym'], "LBIR1300")
        self.assertTrue(attribution_list[1]['start_academic_year'])
        self.assertEqual(attribution_list[1]['start_academic_year'].year, 2015)
        self.assertEqual(attribution_list[1]['end_academic_year'].year,2020)


def _create_multiple_academic_year():
    for year in range(2000,2025):
        AcademicYearFactory(year=year)


def _create_learning_container_with_components(acronym, academic_year, volume_lecturing=None, volume_practical_exercices=None):
    l_container = LearningContainerYearFactory(acronym=acronym, academic_year=academic_year)
    if volume_lecturing:
        LearningComponentYearFactory(
            learning_container_year=l_container,
            type=learning_component_year_type.LECTURING,
            volume_declared_vacant=volume_lecturing
        )
    if volume_practical_exercices:
        LearningComponentYearFactory(
            learning_container_year=l_container,
            type=learning_component_year_type.PRACTICAL_EXERCISES,
            volume_declared_vacant=volume_practical_exercices
        )


def _get_attributions_dict():
    return [
        {'year': 2016, 'acronym': 'LBIR1200', 'title': 'Chimie complexe', 'weight': '5.00', 'LECTURING': '22.5',
         'PRACTICAL_EXERCISES': '5.0', 'function': 'HOLDER', 'start_year': 2015, 'end_year': 2016},
        {'year': 2017, 'acronym': 'LBIR1300', 'title': 'Chimie complexe volume 2', 'weight': '7.50',
         'LECTURING': '12.5', 'PRACTICAL_EXERCISES': '9.5', 'function': 'HOLDER', 'start_year': 2015, 'end_year': 2020},
        {'year': 2017, 'acronym': 'LBIR1200', 'title': 'Chimie complexe', 'weight': '5.00', 'LECTURING': '20.5',
         'PRACTICAL_EXERCISES': '7.0', 'function': 'CO-HOLDER','start_year': 2013}
    ]
