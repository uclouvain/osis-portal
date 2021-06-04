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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
from decimal import Decimal
from time import sleep

from dateutil import parser
from django.contrib.auth.models import Group
from django.test import TestCase, SimpleTestCase

from attribution.business import tutor_application
from attribution.tests.factories.attribution import AttributionNewFactory
from attribution.utils import tutor_application_epc
from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.learning_container_year import LearningContainerYearFactory
from base.tests.factories.learning_unit_year import LearningUnitYearFactory
from base.tests.factories.person import PersonFactory
from base.tests.factories.tutor import TutorFactory


class TutorApplicationTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create academic year
        cls.academic_year = AcademicYearFactory(year=2017)
        # Create several learning container year - 2017
        cls.lbir1200_2017 = LearningContainerYearFactory(academic_year=cls.academic_year, acronym="LBIR1200")
        LearningUnitYearFactory(academic_year=cls.academic_year, learning_container_year=cls.lbir1200_2017)
        cls.lbir1250_2017 = LearningContainerYearFactory(academic_year=cls.academic_year, acronym="LBIR1250")
        LearningUnitYearFactory(academic_year=cls.academic_year, learning_container_year=cls.lbir1250_2017)
        cls.lbir1300_2017 = LearningContainerYearFactory(academic_year=cls.academic_year, acronym="LBIR1300")
        LearningUnitYearFactory(academic_year=cls.academic_year, learning_container_year=cls.lbir1300_2017)
        cls.lagro1200_2017 = LearningContainerYearFactory(academic_year=cls.academic_year, acronym="LAGRO1200")
        LearningUnitYearFactory(academic_year=cls.academic_year, learning_container_year=cls.lagro1200_2017)

        # Create several learning container year - 2016
        cls.academic_year_2016 = AcademicYearFactory(year=2016)
        cls.lbir1200_2016 = LearningContainerYearFactory(academic_year=cls.academic_year_2016, acronym="LBIR1200")
        LearningUnitYearFactory(academic_year=cls.academic_year_2016, learning_container_year=cls.lbir1200_2016)
        cls.lbir1250_2016 = LearningContainerYearFactory(academic_year=cls.academic_year_2016, acronym="LBIR1250")
        LearningUnitYearFactory(academic_year=cls.academic_year_2016, learning_container_year=cls.lbir1250_2016)

        # Creation Person/Tutor
        Group.objects.create(name="tutors")
        cls.person = PersonFactory(global_id="98363454")
        cls.tutor = TutorFactory(person=cls.person)

        cls.applications = [
            _get_application_example(cls.lbir1200_2017, '3.5', '35.6'),  # Application 2017
            _get_application_example(cls.lbir1300_2017, '7.5', '25'),  # Application 2017
            _get_application_example(cls.lbir1200_2016, '2', '30'),  # Application 2016
        ]

    def setUp(self):
        self.attribution = AttributionNewFactory(
            global_id=self.person.global_id,
            attributions=_get_attributions_default(),
            applications=self.applications
        )

    def test_get_application_list(self):
        global_id = self.tutor.person.global_id
        application_list = tutor_application.get_application_list(global_id, self.academic_year)
        self.assertIsInstance(application_list, list)
        self.assertEqual(len(application_list), 2)

        application_list_in_2016 = tutor_application.get_application_list(global_id, self.academic_year_2016)
        self.assertIsInstance(application_list_in_2016, list)
        self.assertEqual(len(application_list_in_2016), 1)

    def test_get_application_list_order_by(self):
        self.attribution.applications = [
            _get_application_example(self.lbir1200_2017, '3.5', '35.6'),  # Application 2017
            _get_application_example(self.lbir1250_2017, '5', '7', tutor_application_epc.UPDATE_OPERATION),
            _get_application_example(self.lbir1300_2017, '7.5', '25')  # Application 2017
        ]
        self.attribution.save()
        global_id = self.tutor.person.global_id
        application_list = tutor_application.get_application_list(global_id, self.academic_year)
        self.assertIsInstance(application_list, list)
        self.assertEqual(len(application_list), 3)
        # Check order
        self.assertEqual(application_list[0]['acronym'], self.lbir1200_2017.acronym)
        self.assertEqual(application_list[1]['acronym'], self.lbir1300_2017.acronym)
        self.assertEqual(application_list[2]['acronym'], self.lbir1250_2017.acronym)


def _get_attributions_default():
    return [
        {
            'year': 2016, 'acronym': 'LBIR1200', 'title': 'Chimie complexe', 'weight': '5.00', 'LECTURING': '22.5',
            'PRACTICAL_EXERCISES': '5.0', 'function': 'HOLDER'
        },
        {
            'year': 2017, 'acronym': 'LBIR1200', 'title': 'Chimie complexe', 'weight': '5.00', 'LECTURING': '20.5',
            'PRACTICAL_EXERCISES': '7.0', 'function': 'CO-HOLDER'
        },
        {
            'year': 2017, 'acronym': 'LBIR1300', 'title': 'Chimie complexe volume 2', 'weight': '7.50',
            'LECTURING': '12.5', 'PRACTICAL_EXERCISES': '9.5', 'function': 'HOLDER'
        },
    ]


def _get_application_example(learning_container_year, volume_lecturing, volume_practical_exercice, flag=None):
    return {
        'remark': 'This is the remarks',
        'course_summary': 'This is the course summary',
        'charge_lecturing_asked': volume_lecturing,
        'charge_practical_asked': volume_practical_exercice,
        'acronym': learning_container_year.acronym,
        'year': learning_container_year.academic_year.year,
        'pending': flag
    }
