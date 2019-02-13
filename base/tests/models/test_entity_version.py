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
import datetime

from django.test import TestCase

from base.models import entity_version
from base.models.enums import organization_type
from base.tests.factories.entity import EntityFactory
from base.tests.factories.entity_version import EntityVersionFactory
from base.tests.factories.organization import OrganizationFactory
from base.models.enums import entity_type

now = datetime.datetime.now()


class EntityVersionTest(TestCase):

    def setUp(self):

        organization = OrganizationFactory(type=organization_type.MAIN)
        self.entities = [EntityFactory( organization=organization) for x in range(2)]

        self.entity_c_older_version = EntityVersionFactory(
            entity=self.entities[0],
            acronym="C ENTITY_V_" + str(0),
            entity_type=entity_type.FACULTY,
            start_date=datetime.date(now.year - 1, 1, 1),
            end_date=datetime.date(now.year - 1, 12, 31)
        )
        self.entity_c_current_version = EntityVersionFactory(
            entity=self.entities[0],
            acronym="B ENTITY_V_" + str(0),
            entity_type=entity_type.FACULTY,
            start_date=datetime.date(now.year, 1, 1),
            end_date=None
        )
        self.entity_a_version = EntityVersionFactory(
            entity=self.entities[1],
            acronym="A ENTITY_V_" + str(1),
            entity_type=entity_type.FACULTY,
            start_date=datetime.date(now.year, 1, 1),
            end_date=None
        )

    def test_search_by_type_current(self):
        self.assertCountEqual(
            list(entity_version.search(
                type=entity_type.FACULTY,
                date=now,
            )),
            [self.entity_a_version, self.entity_c_current_version]
        )

    def test_search_by_type_order(self):
        self.assertEqual(
            list(entity_version.search(
                type=entity_type.FACULTY
            )),
            [self.entity_a_version, self.entity_c_current_version, self.entity_c_older_version]
        )
