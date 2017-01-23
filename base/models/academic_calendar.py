##############################################################################
#
# OSIS stands for Open Student Information System. It's an application
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
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.utils import timezone
from osis_common.models.serializable_model import SerializableModel


class AcademicCalendar(SerializableModel):
    academic_year = models.ForeignKey('AcademicYear')
    title = models.CharField(max_length=50, blank=True, null=True)
    start_date = models.DateField(auto_now=False, blank=True, null=True, auto_now_add=False)
    end_date = models.DateField(auto_now=False, blank=True, null=True, auto_now_add=False)
    reference = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return u"%s %s" % (self.academic_year, self.title)

    class Meta:
        permissions = (
            ("can_access_academic_calendar", "Can access academic calendar"),
        )


def find_academic_calendar(academic_year_id, a_reference, a_date):
    try:
        if academic_year_id and a_reference:
            return AcademicCalendar.objects.get(academic_year=academic_year_id,
                                                reference=a_reference,
                                                start_date__lte=a_date,
                                                end_date__gte=a_date)
    except ObjectDoesNotExist:
        return None
    return None


def is_academic_calendar_opened(an_academic_year_id, a_reference):
    an_academic_calendar = find_academic_calendar(an_academic_year_id,
                                                  a_reference,
                                                  timezone.now())
    if an_academic_calendar:
        return True
    return False
