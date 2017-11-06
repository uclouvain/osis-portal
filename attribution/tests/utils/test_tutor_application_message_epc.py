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
from django.test import TestCase

from attribution.utils import tutor_application_message_epc
from base.models.academic_year import AcademicYear
from base.tests.factories.learning_container_year import LearningContainerYearFactory


class TestTutorApplicationMessageEpc(TestCase):
    def setUp(self):
        self.academic_year = AcademicYear.objects.get(year=2017)
        external_id = tutor_application_message_epc.LEARNING_CONTAINER_YEAR_PREFIX_EXTERNAL_ID + '35654987_2017'
        self.lbir1200 = LearningContainerYearFactory(academic_year=self.academic_year, acronym="LBIR1200", external_id=external_id)
        self.lbir1230 = LearningContainerYearFactory(academic_year=self.academic_year, acronym="LBIR1230")

    def test_extract_learning_container_year_epc_info(self):
        learning_container_info = tutor_application_message_epc._extract_learning_container_year_epc_info('LBIR1200', 2017)
        self.assertIsInstance(learning_container_info, dict)
        self.assertEqual(learning_container_info['reference'], '35654987')
        self.assertEqual(learning_container_info['year'], '2017')

    def test_extract_learning_container_year_epc_info_empty(self):
        learning_container_info = tutor_application_message_epc._extract_learning_container_year_epc_info('LBIR1250', 2017)
        self.assertIsInstance(learning_container_info, dict)
        self.assertFalse(learning_container_info)

    def test_extract_learning_container_year_epc_info_with_external_id_empty(self):
        learning_container_info = tutor_application_message_epc._extract_learning_container_year_epc_info('LBIR1230', 2017)
        self.assertIsInstance(learning_container_info, dict)
        self.assertFalse(learning_container_info)
