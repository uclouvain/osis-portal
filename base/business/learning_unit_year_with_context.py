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
from collections import OrderedDict

from django.db import models

from base import models as mdl
from base.models.enums import entity_container_year_link_type as entity_types
from base.models.enums.learning_unit_year_subtypes import FULL
from base.models.learning_component_year import LearningComponentYear
from osis_common.utils.numbers import to_float_or_zero


class LearningUnitYearWithContext:
    def __init__(self, **kwargs):
        self.learning_unit_year = kwargs.get('learning_unit_year')


def get_with_context(**learning_unit_year_data):
    entity_container_prefetch = models.Prefetch(
        'learning_container_year__entitycontaineryear_set',
        queryset=mdl.entity_container_year
            .search(
            link_type=[
                entity_types.REQUIREMENT_ENTITY,
                entity_types.ALLOCATION_ENTITY,
                entity_types.ADDITIONAL_REQUIREMENT_ENTITY_1,
                entity_types.ADDITIONAL_REQUIREMENT_ENTITY_2
            ]
        )
            .prefetch_related(
            models.Prefetch('entity__entityversion_set', to_attr='entity_versions')
        ),
        to_attr='entity_containers_year'
    )

    learning_component_prefetch = models.Prefetch(
        'learningcomponentyear_set',
        queryset=LearningComponentYear.objects.all().order_by('type', 'acronym'),
        to_attr='learning_components'
    )

    learning_units = mdl.learning_unit_year.LearningUnitYear.objects.filter(subtype=FULL, **learning_unit_year_data) \
        .select_related('academic_year', 'learning_container_year') \
        .prefetch_related(entity_container_prefetch) \
        .prefetch_related(learning_component_prefetch) \
        .order_by('academic_year__year', 'acronym')

    learning_units = [append_latest_entities(learning_unit) for learning_unit in learning_units]
    learning_units = [_append_components(learning_unit) for learning_unit in learning_units]

    return learning_units


def append_latest_entities(learning_unit):
    learning_unit.entities = {}
    learning_container_year = learning_unit.learning_container_year

    for entity_container_yr in getattr(learning_container_year, "entity_containers_year", []):
        link_type = entity_container_yr.type
        learning_unit.entities[link_type] = entity_container_yr.get_latest_entity_version()

    return learning_unit


def _append_components(learning_unit_year):
    learning_unit_year.components = OrderedDict()
    if learning_unit_year.learning_components:
        for component in learning_unit_year.learning_components:
            req_entities_volumes = _get_requirement_entities_volumes(component)
            vol_req_entity = req_entities_volumes.get(entity_types.REQUIREMENT_ENTITY, 0) or 0
            vol_add_req_entity_1 = req_entities_volumes.get(entity_types.ADDITIONAL_REQUIREMENT_ENTITY_1, 0) or 0
            vol_add_req_entity_2 = req_entities_volumes.get(entity_types.ADDITIONAL_REQUIREMENT_ENTITY_2, 0) or 0
            volume_global = vol_req_entity + vol_add_req_entity_1 + vol_add_req_entity_2
            planned_classes = component.planned_classes or 0

            learning_unit_year.components[component] = {
                'VOLUME_TOTAL': to_float_or_zero(component.hourly_volume_total_annual),
                'VOLUME_Q1': to_float_or_zero(component.hourly_volume_partial_q1),
                'VOLUME_Q2': to_float_or_zero(component.hourly_volume_partial_q2),
                'PLANNED_CLASSES': planned_classes,
                'VOLUME_' + entity_types.REQUIREMENT_ENTITY: vol_req_entity,
                'VOLUME_' + entity_types.ADDITIONAL_REQUIREMENT_ENTITY_1: vol_add_req_entity_1,
                'VOLUME_' + entity_types.ADDITIONAL_REQUIREMENT_ENTITY_2: vol_add_req_entity_2,
                'VOLUME_TOTAL_REQUIREMENT_ENTITIES': volume_global,
            }
    return learning_unit_year


def _get_requirement_entities_volumes(learning_component):
    return {
        key: value for key, value in learning_component.repartition_volumes.items()
    }
