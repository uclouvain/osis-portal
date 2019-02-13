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
import collections

from django.db import models, connection
from django.db.models import Q
from django.db import models
from base.models.enums import entity_type
from osis_common.models.serializable_model import SerializableModel, SerializableModelAdmin
from django.utils.translation import ugettext_lazy as _
from django.utils.timezone import now
from base.models.entity import Entity


SQL_RECURSIVE_QUERY = """\
WITH RECURSIVE under_entity AS (

    SELECT id, acronym, parent_id, entity_id, '{{}}'::INT[] AS parents, '{date}'::DATE AS date, 0 AS level
    FROM base_entityversion WHERE entity_id IN ({list_entities})

    UNION ALL

    SELECT b.id,
           b.acronym,
           b.parent_id,
           b.entity_id,
           parents || b.parent_id,
           u.date,
           u.level + 1

    FROM under_entity AS u, base_entityversion AS b
    WHERE (u.entity_id=b.parent_id) AND (
        (b.end_date >= date::date OR b.end_date IS NULL) AND
        b.start_date <= date::date)
    )

SELECT * FROM under_entity ;
"""


class EntityVersionAdmin(SerializableModelAdmin):
    list_display = ('id', 'entity', 'acronym', 'parent')
    search_fields = ['entity__id']
    raw_id_fields = ('entity', 'parent')


class EntityVersionQuerySet(models.QuerySet):
    def current(self, date):
        if date:
            return self.filter(Q(end_date__gte=date) | Q(end_date__isnull=True), start_date__lte=date)
        else:
            return self

    def entity(self, entity):
        return self.filter(entity=entity)

    def get_tree(self, entities, date=None):
        """
        Create a list of all descendants of given entities

        :param entities: int, Entity, QuerysetEntity, [int], [Entity]
        :param date: Date
        :return: list(dict))
        """
        list_entities_id = []

        if not date:
            date = now()

        # Convert the entity in list
        if not isinstance(entities, collections.Iterable):
            entities = [entities]

        # Extract from the list the ids
        for entity in entities:
            if isinstance(entity, Entity):
                entity = entity.pk

            list_entities_id.append(str(entity))

        with connection.cursor() as cursor:
            cursor.execute(SQL_RECURSIVE_QUERY.format(list_entities=','.join(list_entities_id), date=date))

            return [
                {
                    'id': row[0],
                    'acronym': row[1],
                    'parent_id': row[2],
                    'entity_id': row[3],
                    'parents': row[4],
                    'date': row[5],
                    'level': row[6],
                } for row in cursor.fetchall()
                ]


class EntityVersion(SerializableModel):
    changed = models.DateTimeField(null=True, auto_now=True)
    entity = models.ForeignKey('Entity')
    acronym = models.CharField(db_index=True, max_length=20, null=True, blank=True)
    entity_type = models.CharField(
        choices=entity_type.ENTITY_TYPES,
        max_length=50,
        db_index=True,
        blank=True,
        verbose_name=_("Type")
    )
    parent = models.ForeignKey('Entity', related_name='parent_of', blank=True, null=True)
    start_date = models.DateField(db_index=True)
    end_date = models.DateField(db_index=True, blank=True, null=True)

    objects = EntityVersionQuerySet.as_manager()

    def __str__(self):
        return "{}".format(
            self.acronym,
        )


def search(**kwargs):
    queryset = EntityVersion.objects

    if 'entity_type' in kwargs:
        queryset = queryset.filter(entity_type__exact=kwargs['entity_type'])

    if 'date' in kwargs:
        a_date = kwargs['date']
        queryset = queryset.filter(Q(start_date__lte=a_date,
                                   end_date__gte=a_date) |
                                   Q(start_date__lte=a_date, end_date__isnull=True))

    return queryset.order_by('acronym')
