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

from django.core.exceptions import ObjectDoesNotExist
from django.db import connection
from django.test import TestCase
from django.contrib.auth.models import Group

from attribution import models as mdl_attribution
from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.learning_unit_year import LearningUnitYearFactory
from base.tests.factories.tutor import TutorFactory
from attribution.tests.factories.attribution import AttributionFactory
from base.tests.models import test_person
from base.tests.factories.user import UserFactory
from attribution.models.enums import function


def create_attribution(data):
    attribution = mdl_attribution.attribution.Attribution()
    start = None
    if 'start_year' in data:
        start = data['start_year']
    end = None
    if 'end_year' in data:
        end = data['end_year']
    if 'function' in data:
        attribution.function = data['function']
    if 'learning_unit_year' in data:
        attribution.learning_unit_year = data['learning_unit_year']
        year_yr = attribution.learning_unit_year.academic_year.year
        if start is None:
            attribution.start_year = year_yr
        if end is None:
            attribution.end_year = year_yr+1
    if start:
        attribution.start_year = start
    if end:
        attribution.end_year = end
    if 'tutor' in data:
        attribution.tutor = data['tutor']
    if 'external_id' in data:
        attribution.external_id = data['external_id']
    attribution.save()
    return attribution


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

    def test_attribution_deleted_field(self):
        attribution_id = self.attribution.id

        with connection.cursor() as cursor:
            cursor.execute("update attribution_attribution set deleted=True where id=%s", [attribution_id])

        with self.assertRaises(ObjectDoesNotExist):
            mdl_attribution.attribution.Attribution.objects.get(id=attribution_id)

        with connection.cursor() as cursor:
            cursor.execute("select id, deleted from attribution_attribution where id=%s", [attribution_id])
            row = cursor.fetchone()
            db_attribution_id = row[0]
            db_attribution_deleted = row[1]
        self.assertEqual(db_attribution_id, attribution_id)
        self.assertTrue(db_attribution_deleted)

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
        self.assertListEqual(list(mdl_attribution.attribution.find_by_tutor_year_order_by_acronym_function(self.tutor, self.an_academic_year)), [a_attribution, c_attribution, b_attribution])

