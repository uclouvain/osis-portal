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

from django.test import TestCase

from attribution import models as mdl_attribution
from base.tests.factories.academic_year import AcademicYearFactory
from attribution.tests.factories.attribution import AttributionNewFactory
from base.tests.models import test_person
from base.tests.factories.user import UserFactory

LCHM1111 = 'LCHM1111'
YEAR_2016 = 2016
YEAR_2017 = 2017


class AttributionNewTest(TestCase):
    def setUp(self):
        # group = Group(name="tutors")
        # group.save()
        # self.attribution = AttributionFactory()
        today = datetime.datetime.today()
        self.an_academic_year = AcademicYearFactory(year=today.year)
        self.user = UserFactory()
        self.person = test_person.create_person_with_user(self.user)
        # self.tutor = TutorFactory(person=self.person)

    def test_find_no_attribution(self):
        AttributionNewFactory(global_id="123456789",
                              attributions=[])
        results = mdl_attribution.attribution_new.find_teachers(LCHM1111, YEAR_2017)
        self.assertEquals(len(results), 0)

    def test_find_no_teachers_for_acronym(self):
        AttributionNewFactory(global_id="123456789",
                              attributions=[{'year': YEAR_2017, 'acronym': LCHM1111}])
        results = mdl_attribution.attribution_new.find_teachers("{}Z".format(LCHM1111), YEAR_2017)
        self.assertEquals(len(results), 0)

    def test_find_no_teachers_for_year(self):
        AttributionNewFactory(global_id="123456789",
                              attributions=[{'year': YEAR_2017, 'acronym': LCHM1111}])
        results = mdl_attribution.attribution_new.find_teachers(LCHM1111, YEAR_2016)
        self.assertEquals(len(results), 0)

    def test_find_teachers(self):
        build_attributions_for_2_teachers_on_a_learning_unit(LCHM1111, YEAR_2017)
        results = mdl_attribution.attribution_new.find_teachers(LCHM1111, YEAR_2017)
        self.assertEquals(len(results), 2)


def build_attributions_for_2_teachers_on_a_learning_unit(an_acronym, yr):
    attributionLCHM1111 = {'year': yr, 'acronym': an_acronym}

    AttributionNewFactory(global_id="123456789",
                          attributions=[
                              attributionLCHM1111,
                              {'year': YEAR_2016, 'acronym': 'LDVLP2627'},
                              {'year': yr, 'acronym': 'LDVLP2627'},
                              {'year': yr, 'acronym': 'LDROI1110'}])
    AttributionNewFactory(global_id="987654321",
                          attributions=[
                              attributionLCHM1111,
                              {'year': YEAR_2016, 'acronym': 'LAGRO1256'}])
