##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
from django.db import models
from osis_common.models.serializable_model import SerializableModelAdmin, SerializableModel


class CohortAdmin(SerializableModelAdmin):
    list_display = ('name', 'description', 'free_internships_number', 'publication_start_date',
                    'subscription_start_date', 'subscription_end_date')
    fieldsets = ((None, {'fields': ('name', 'description', 'free_internships_number', 'publication_start_date',
                                    'subscription_start_date', 'subscription_end_date')}),)


class Cohort(SerializableModel):
    name = models.CharField(max_length=255, blank=False)
    description = models.TextField()
    free_internships_number = models.IntegerField(blank=False)
    publication_start_date = models.DateField(blank=False)
    subscription_start_date = models.DateField(blank=False)
    subscription_end_date = models.DateField(blank=False)

    def __str__(self):
        return u"%s" % self.name
