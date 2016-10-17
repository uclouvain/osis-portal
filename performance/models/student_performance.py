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
from django.contrib.postgres.fields import JSONField
from django.contrib import admin
from django.core.exceptions import ObjectDoesNotExist
from base.models.serializable_model import SerializableModel
from performance.queue.student_performance import fetch_and_save, fetch_and_update
import datetime


class StudentPerformanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'offer_year', 'update_date', 'creation_date')
    list_filter = ('student__registration_id',)
    fieldsets = ((None, {'fields': ('student', 'offer_year', 'update_date', 'creation_date')}),)


class StudentPerformance(SerializableModel):
    student = models.ForeignKey('base.Student')
    offer_year = models.ForeignKey('base.OfferYear')
    data = JSONField()
    update_date = models.DateField()
    creation_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return


def search(student=None, offer_year=None):
    """
        Search students by optional arguments. At least one argument should be informed
        otherwise it returns empty.
    """
    has_criteria = False
    student_performances = StudentPerformance.objects
    if student:
        student_performances.filter(student=student)
        has_criteria = True
    if offer_year:
        student_performances.filter(offer_year=offer_year)
        has_criteria = True

    if has_criteria:
        return student_performances
    else:
        return None


def find_by_student_and_offer_year(student, offer_year):
    try:
        result = StudentPerformance.objects.get(student=student, offer_year=offer_year)
    except ObjectDoesNotExist:
        result = None
    return result


def find_or_fetch(student, offer_year):
    result = find_by_student_and_offer_year(student, offer_year)
    if result is None:
        result = fetch_and_save(student, offer_year)
    elif has_expired(result):
        fetch_and_update(result)
    return result


def has_expired(student_performance):
    today = datetime.date.today()
    expiration_date = student_performance.update_date
    return expiration_date < today


