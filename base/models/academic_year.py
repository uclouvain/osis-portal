##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2017 Université catholique de Louvain (http://www.uclouvain.be)
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
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from osis_common.models.serializable_model import SerializableModel, SerializableModelAdmin


class AcademicYearAdmin(SerializableModelAdmin):
    list_display = ('name', 'start_date', 'end_date')
    fieldsets = ((None, {'fields': ('year', 'start_date', 'end_date')}),)


class AcademicYear(SerializableModel):
    external_id = models.CharField(max_length=100, blank=True, null=True)
    year = models.IntegerField()
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)

    @property
    def name(self):
        return self.__str__()

    def __str__(self):
        return u"%s-%s" % (self.year, str(self.year + 1)[-2:])


def find_academic_years(start_date=None, end_date=None):
    queryset = AcademicYear.objects.all()
    if start_date is not None:
        queryset = queryset.filter(start_date__lte=start_date)
    if end_date is not None:
        queryset = queryset.filter(end_date__gte=end_date)

    return queryset.order_by('year')


def current_academic_years():
    now = timezone.now()
    return find_academic_years(start_date=now, end_date=now)


def current_academic_year():
    """ If we have two academic year [2015-2016] [2016-2017]. It will return [2015-2016] """
    return current_academic_years().first()


def starting_academic_year():
    """ If we have two academic year [2015-2016] [2016-2017]. It will return [2016-2017] """
    return current_academic_years().last()


def find_by_year(a_year):
    try:
        return AcademicYear.objects.get(year=a_year)
    except ObjectDoesNotExist:
        return None


def find_next_academic_year():
    academic_yr = current_academic_year()
    if academic_yr:
        return academic_yr.year + 1
    else:
        return None
