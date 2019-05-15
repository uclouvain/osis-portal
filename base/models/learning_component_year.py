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
from base.models.enums import learning_component_year_type
from django.db import models

from base.models.enums.entity_container_year_link_type import REQUIREMENT_ENTITY, ADDITIONAL_REQUIREMENT_ENTITY_1, \
    ADDITIONAL_REQUIREMENT_ENTITY_2
from osis_common.models.serializable_model import SerializableModelAdmin, SerializableModel


class LearningComponentYearAdmin(SerializableModelAdmin):
    list_display = ('learning_unit_year', 'acronym', 'type', 'volume_declared_vacant', 'planned_classes')
    fieldsets = ((None, {'fields': ('learning_unit_year', 'acronym', 'type', 'volume_declared_vacant',
                                    'planned_classes', 'hourly_volume_total_annual', 'hourly_volume_partial_q1',
                                    'hourly_volume_partial_q2')}),)
    search_fields = ['acronym', 'learning_unit_year__acronym']
    raw_id_fields = ('learning_unit_year',)
    list_filter = ('learning_unit_year__academic_year',)


class RepartitionVolumeField(models.DecimalField):
    def __init__(self, *args, **kwargs):
        super(RepartitionVolumeField, self).__init__(*args, **kwargs)
        self.blank = self.null = True
        self.max_digits = 6
        self.decimal_places = 2


class LearningComponentYear(SerializableModel):
    external_id = models.CharField(max_length=100, blank=True, null=True)
    changed = models.DateTimeField(null=True, auto_now=True)
    learning_unit_year = models.ForeignKey('LearningUnitYear')
    acronym = models.CharField(max_length=4, blank=True, null=True)
    type = models.CharField(max_length=30, choices=learning_component_year_type.LEARNING_COMPONENT_YEAR_TYPES,
                            blank=True, null=True, db_index=True)
    planned_classes = models.IntegerField(blank=True, null=True)
    hourly_volume_total_annual = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    hourly_volume_partial_q1 = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    hourly_volume_partial_q2 = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    volume_declared_vacant = models.DecimalField(max_digits=6, decimal_places=1, blank=True, null=True)

    repartition_volume_requirement_entity = RepartitionVolumeField()
    repartition_volume_additional_entity_1 = RepartitionVolumeField()
    repartition_volume_additional_entity_2 = RepartitionVolumeField()

    def __str__(self):
        return u"%s - %s" % (self.acronym, self.learning_unit_year.acronym)

    @property
    def repartition_volumes(self):
        # TODO:: add unit tests
        default_value = 0.0
        return {
            REQUIREMENT_ENTITY: float(self.repartition_volume_requirement_entity or default_value),
            ADDITIONAL_REQUIREMENT_ENTITY_1: float(self.repartition_volume_additional_entity_1 or default_value),
            ADDITIONAL_REQUIREMENT_ENTITY_2: float(self.repartition_volume_additional_entity_2 or default_value),
        }

