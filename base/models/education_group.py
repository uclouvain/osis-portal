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

from base.models import offer_enrollment
from osis_common.models.serializable_model import SerializableModelAdmin, SerializableModel


class EducationGroupAdmin(SerializableModelAdmin):
    list_display = ('most_recent_acronym', 'start_year', 'end_year',)
    search_fields = ('educationgroupyear__acronym',)


class EducationGroup(SerializableModel):
    external_id = models.CharField(max_length=100, blank=True, null=True)
    start_year = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name=_('Start')
    )

    end_year = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name=_('End')
    )

    def __str__(self):
        return "{}".format(self.uuid)

    @property
    def most_recent_acronym(self):
        most_recent_education_group = self.educationgroupyear_set.filter(education_group_id=self.id) \
            .latest('academic_year__year')
        return most_recent_education_group.acronym

def find_by_student(student):
    educ_goup_ids = offer_enrollment.find_by_student(student).values('education_group_year__education_group_id')
    return EducationGroup.objects.filter(pk__in=educ_goup_ids)
