##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
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

from django.contrib.auth.models import Group
from django.test import TestCase

from attribution import models as mdl_attribution
from attribution.models.enums import function
from attribution.tests.factories.attribution import AttributionFactory
from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.learning_unit_year import LearningUnitYearFactory
from base.tests.factories.tutor import TutorFactory
from base.tests.factories.user import UserFactory
from base.tests.models import test_person


class AttributionTest(TestCase):
    def setUp(self):
        group = Group(name="tutors")
        group.save()
        self.attribution = AttributionFactory()
        today = datetime.datetime.today()
        self.an_academic_year = AcademicYearFactory(year=today.year)
        self.user = UserFactory()
        self.person = test_person.create_person_with_user(self.user)
        self.tutor = TutorFactory(person=self.person)

    def test_find_by_tutor_year_order_by_acronym_function_check_alphabetical_order(self):
        a_learning_unit_year = LearningUnitYearFactory(academic_year=self.an_academic_year, acronym='LAUT')
        b_learning_unit_year = LearningUnitYearFactory(academic_year=self.an_academic_year, acronym='LBUT')
        a_attribution = self.attribution = AttributionFactory(tutor=self.tutor,
                                                              function=function.HOLDER,
                                                              learning_unit_year=a_learning_unit_year)
        b_attribution = self.attribution = AttributionFactory(tutor=self.tutor,
                                                              function=function.HOLDER,
                                                              learning_unit_year=b_learning_unit_year)
        c_attribution = self.attribution = AttributionFactory(tutor=self.tutor,
                                                              function=function.CO_HOLDER,
                                                              learning_unit_year=b_learning_unit_year)
        self.assertListEqual(list(mdl_attribution.attribution.find_by_tutor_year_order_by_acronym_function(self.tutor,
                                                                                                           self.an_academic_year)),
                             [a_attribution, c_attribution, b_attribution])

    def test_is_summary_responsible_tutor(self):
        self.attribution = AttributionFactory(tutor=self.tutor,
                                              summary_responsible=True)
        return self.assertTrue(mdl_attribution.attribution.is_summary_responsible(self.tutor))

    def test_is_not_summary_responsible_tutor(self):
        self.attribution = AttributionFactory(tutor=self.tutor,
                                              summary_responsible=False)
        return self.assertFalse(mdl_attribution.attribution.is_summary_responsible(self.tutor))
