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

from osis_common.models.serializable_model import SerializableModel, SerializableModelAdmin
from reference.enums import grade_type_coverage
from reference.enums import institutional_grade_type as enum_institutional_grade_type


class GradeTypeAdmin(SerializableModelAdmin):
    list_display = ('name', 'institutional_grade_type', 'coverage', 'adhoc', 'institutional')
    fieldsets = ((None, {'fields': ('name', 'institutional_grade_type', 'coverage', 'adhoc', 'institutional')}),)


class GradeType(SerializableModel):
    external_id = models.CharField(max_length=100, blank=True, null=True)
    name = models.CharField(max_length=255)
    coverage = models.CharField(max_length=30,
                                choices=grade_type_coverage.COVERAGES,
                                default=grade_type_coverage.UNKNOWN)
    adhoc = models.BooleanField(default=True)  # If False == Official/validated, if True == Not Official/not validated
    institutional = models.BooleanField(default=False)  # True if the domain is in UCL else False
    institutional_grade_type = models.CharField(max_length=25,
                                                choices=enum_institutional_grade_type.INSTITUTIONAL_GRADE_CHOICES,
                                                blank=True,
                                                null=True)

    def __str__(self):
        return self.name
