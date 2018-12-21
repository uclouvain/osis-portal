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
from django.db import models
from django.db.models import Q
from django.db import models
from base.models.enums import entity_type
from osis_common.models.serializable_model import SerializableModel, SerializableModelAdmin
from django.utils.translation import ugettext_lazy as _
from osis_common.utils.datetime import get_tzinfo


class EntityVersionAdmin(SerializableModelAdmin):
    list_display = ('id', 'entity', 'acronym', 'parent' )
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

    def find_faculty_version(self, academic_yr):
        if self.entity_type == entity_type.FACULTY:
            return self
        # There is no faculty above the sector
        elif self.entity_type == entity_type.SECTOR:
            return None
        else:
            parent_entity_version = self._find_latest_version_by_parent(academic_yr.start_date)
            if parent_entity_version:
                return parent_entity_version.find_faculty_version(academic_yr)

    def _find_latest_version_by_parent(self, start_date):
        if not self.parent:
            return None

        # if a prefetch exist on the parent
        entity_versions = getattr(self.parent, 'entity_versions', None)
        if not entity_versions:
            return find_latest_version_by_entity(self.parent, start_date)

        for entity_version in entity_versions:
            if entity_version.__contains_given_date(start_date):
                return entity_version

def search(**kwargs):
    queryset = EntityVersion.objects

    if 'entity_type' in kwargs:
        queryset = queryset.filter(entity_type__exact=kwargs['entity_type'])


    return queryset

def get_last_version_by_entity_id(entity_id):
    now = datetime.datetime.now(get_tzinfo())
    res = EntityVersion.objects.current(now).filter(entity__id=entity_id)
    if res:
        return res.latest('start_date')
    return None

def find_latest_version_by_entity(entity, date):
    return EntityVersion.objects.current(date).entity(entity).select_related('entity', 'parent').first()
