##############################################################################
#
# OSIS stands for Open Student Information System. It's an application
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

import factory
import factory.fuzzy
from django.test import TestCase
from django.utils import timezone

from base.models.entity_version import EntityVersion
from base.models.enums import entity_type
from base.tests.factories.entity import EntityFactory
from base.tests.factories.entity_version import EntityVersionFactory


class EntityTest(TestCase):

    def setUp(self):
        self.start_date = timezone.make_aware(datetime.datetime(2015, 1, 1))
        self.end_date = timezone.make_aware(datetime.datetime(2015, 12, 31))
        self.date_in_2015 = factory.fuzzy.FuzzyDate(timezone.make_aware(datetime.datetime(2015, 1, 1)),
                                                    timezone.make_aware(datetime.datetime(2015, 12, 30))).fuzz()
        self.date_in_2017 = factory.fuzzy.FuzzyDate(timezone.make_aware(datetime.datetime(2017, 1, 1)),
                                                    timezone.make_aware(datetime.datetime(2017, 12, 30))).fuzz()
        self.parent = EntityFactory()
        EntityVersionFactory(
            entity=self.parent,
            parent=None,
            acronym="ROOT_ENTITY",
            start_date=self.start_date,
            end_date=self.end_date
        )
        self.children = [EntityFactory() for x in range(4)]
        self.types_dict = dict(entity_type.ENTITY_TYPES)
        types = [self.types_dict['SECTOR'],
                 self.types_dict['FACULTY'],
                 self.types_dict['SCHOOL'],
                 self.types_dict['FACULTY']]

        for x in range(4):
            EntityVersionFactory(
                entity=self.children[x],
                parent=self.parent,
                acronym="ENTITY_V_" + str(x),
                start_date=self.start_date,
                end_date=self.end_date,
                entity_type=types[x]
                )

    def test_find_descendants_with_parent(self):
        entities_with_descendants = EntityVersion.objects.get_tree([self.parent], date=self.date_in_2015)
        self.assertEqual(len(entities_with_descendants), 5)

    def test_find_descendants_out_date(self):
        entities_with_descendants = EntityVersion.objects.get_tree([self.parent], date=self.date_in_2017)
        self.assertEqual(len(entities_with_descendants), 1)

    def test_find_descendants_with_multiple_parent(self):
        parent_2 = EntityFactory()
        EntityVersionFactory(entity=parent_2, parent=None, acronym="ROOT_ENTITY_2", start_date=self.start_date,
                             end_date=self.end_date)
        ### Create one child entity with parent ROOT_ENTITY_2
        child = EntityFactory()
        EntityVersionFactory(entity=child, parent=parent_2, acronym="CHILD_OF_ROOT_2", start_date=self.start_date,
                             end_date=self.end_date)
        ### Create one child entity with parent CHILD_OF_ROOT_2
        child_2 = EntityFactory()
        EntityVersionFactory(entity=child_2, parent=child, acronym="CHILD_OF_CHILD", start_date=self.start_date,
                             end_date=self.end_date)
        entities_with_descendants = EntityVersion.objects.get_tree([self.parent, parent_2], date=self.date_in_2015)
        self.assertEqual(len(entities_with_descendants), 8)# 5 for parent + 3 for parent_2

    def test_most_recent_acronym(self):
        entity_instance = EntityFactory()
        most_recent_year = 2018
        for year in range(2016, most_recent_year + 1):
            date = datetime.date(year=year, month=1, day=1)
            EntityVersionFactory(entity_id=entity_instance.id, start_date=date)
        most_recent_date = datetime.date(year=most_recent_year, month=1, day=1)
        most_recent_entity_version = EntityVersion.objects.get(start_date=most_recent_date,
                                                               entity=entity_instance)
        self.assertEqual(entity_instance.most_recent_acronym, most_recent_entity_version.acronym)

    def test_most_recent_acronym_not_found(self):
        entity_instance = EntityFactory()
        self.assertEqual(entity_instance.most_recent_acronym, None)
