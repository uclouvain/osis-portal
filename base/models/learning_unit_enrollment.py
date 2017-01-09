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
from django.contrib import admin
from osis_common.models.serializable_model import SerializableModel


class LearningUnitEnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'learning_unit_year', 'date_enrollment', 'changed')
    fieldsets = ((None, {'fields': ('offer_enrollment', 'learning_unit_year', 'date_enrollment')}),)
    list_filter = ('learning_unit_year__academic_year__year',)
    raw_id_fields = ('offer_enrollment', 'learning_unit_year')
    search_fields = ['learning_unit_year__acronym']


class LearningUnitEnrollment(SerializableModel):
    external_id = models.CharField(max_length=100, blank=True, null=True)
    changed = models.DateTimeField(null=True)
    date_enrollment = models.DateField()
    learning_unit_year = models.ForeignKey('LearningUnitYear')
    offer_enrollment = models.ForeignKey('OfferEnrollment')

    @property
    def student(self):
        return self.offer_enrollment.student

    @property
    def offer(self):
        return self.offer_enrollment.offer_year

    def __str__(self):
        return u"%s - %s" % (self.learning_unit_year, self.offer_enrollment.student)


def find_by_learningunit_enrollment(learning_unit_year):
    return LearningUnitEnrollment.objects.filter(learning_unit_year=learning_unit_year).order_by('offer_enrollment__student__person__last_name',
                                                                                                 'offer_enrollment__student__person__first_name')
