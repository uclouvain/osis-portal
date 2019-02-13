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

from osis_common.models.serializable_model import SerializableModel, SerializableModelAdmin


class EducationGroupYearAdmin(SerializableModelAdmin):
    list_display = ('acronym', 'title', 'academic_year', 'education_group_type',)
    list_filter = ('academic_year', 'education_group_type',)
    search_fields = ['acronym']


class EducationGroupYear(SerializableModel):
    external_id = models.CharField(max_length=100, blank=True, null=True)
    acronym = models.CharField(
        max_length=40,
        db_index=True,
        verbose_name=_("Acronym"),
    )

    partial_acronym = models.CharField(
        max_length=15,
        db_index=True,
        null=True,
        verbose_name=_("Code"),
    )

    title = models.CharField(
        max_length=255,
        verbose_name=_("Title in French"),
    )

    academic_year = models.ForeignKey(
        'AcademicYear',
        verbose_name=_("Validity"),
    )

    education_group = models.ForeignKey(
        'EducationGroup',
        on_delete=models.CASCADE
    )

    education_group_type = models.ForeignKey(
        'EducationGroupType',
        verbose_name=_("Type of training")
    )

    dissertation = models.BooleanField(
        default=False,
        verbose_name=_('dissertation')
    )

    management_entity = models.ForeignKey(
        'Entity',
        verbose_name=_("Management entity"),
        null=True,
        related_name="management_entity"
    )

    administration_entity = models.ForeignKey(
        'Entity',
        null=True,
        verbose_name=_("Administration entity"),
        related_name='administration_entity'
    )

    class Meta:
        verbose_name = _("Education group year")
        unique_together = ('education_group', 'academic_year')

    def __str__(self):
        return "{} - {} - {}".format(
            self.partial_acronym,
            self.acronym,
            self.academic_year,
        )


def find_by_education_groups(education_groups):
    return EducationGroupYear.objects.filter(education_group__in=education_groups)
