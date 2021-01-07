##############################################################################
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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
from django.test import TestCase

from base.models.enums import learning_container_type
from base.tests.factories.learning_container_year import LearningContainerYearFactory

IN_CHARGE_TYPES = [learning_container_type.COURSE, learning_container_type.DISSERTATION,
                   learning_container_type.INTERNSHIP]
NOT_IN_CHARGE_TYPES = [learning_container_type.OTHER_COLLECTIVE, learning_container_type.OTHER_INDIVIDUAL,
                       learning_container_type.MASTER_THESIS, learning_container_type.EXTERNAL]


class LearningContainerYearTestCase(TestCase):

    def test_in_charge(self):
        for type in IN_CHARGE_TYPES:
            l_c_yr = LearningContainerYearFactory(container_type=type)
            self.assertTrue(l_c_yr.in_charge)

    def test_not_in_charge(self):
        for type in NOT_IN_CHARGE_TYPES:
            l_c_yr = LearningContainerYearFactory(container_type=type)
            self.assertFalse(l_c_yr.in_charge)
