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
from django.db import models
from django.utils.translation import ugettext_lazy as _

from base.models.enums import education_group_categories
from osis_common.models.serializable_model import SerializableModelAdmin, SerializableModel


class EducationGroupTypeAdmin(SerializableModelAdmin):
    list_display = ('name', 'category',)
    list_filter = ('name', 'category',)
    search_fields = ['name', 'category']


class EducationGroupType(SerializableModel):
    external_id = models.CharField(max_length=100, blank=True, null=True)
    category = models.CharField(
        max_length=25,
        choices=education_group_categories.CATEGORIES,
        default=education_group_categories.TRAINING,
        verbose_name=_('Category'),
    )

    name = models.CharField(
        max_length=255,
        verbose_name=_('Type of training'),
    )

    def __str__(self):
        return u"%s" % self.name
