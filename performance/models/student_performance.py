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
from django.contrib import admin
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models import JSONField
from django.utils import timezone

from performance.models.enums import offer_registration_state, session_month
from performance.queue.student_performance import fetch_and_save


class StudentPerformanceAdmin(admin.ModelAdmin):
    list_display = ('registration_id', 'academic_year',
                    'acronym', 'update_date', 'creation_date', 'authorized', 'offer_registration_state',
                    'courses_registration_validated', 'learning_units_outside_catalog')
    list_filter = ('academic_year',)
    fieldsets = ((None, {
        'fields': ('registration_id', 'academic_year', 'acronym', 'update_date',
                   'creation_date', 'data', 'courses_registration_validated',
                   'learning_units_outside_catalog', 'course_registration_message', 'on_site_exams_info')
    }),)
    readonly_fields = ('creation_date', 'courses_registration_validated', 'learning_units_outside_catalog',
                       'on_site_exams_info')

    search_fields = ['registration_id', 'academic_year', 'acronym']


class StudentPerformance(models.Model):
    registration_id = models.CharField(max_length=10, db_index=True)
    academic_year = models.IntegerField()
    acronym = models.CharField(max_length=15)
    data = JSONField()
    update_date = models.DateTimeField()
    creation_date = models.DateTimeField()
    authorized = models.BooleanField(default=True)

    offer_registration_state = models.CharField(
        max_length=50,
        choices=offer_registration_state.OFFER_REGISTRATION_STATES,
        null=True
    )

    session_locked = models.CharField(
        max_length=50,
        choices=session_month.SESSION_MONTHS,
        null=True
    )

    courses_registration_validated = models.BooleanField(null=True)
    learning_units_outside_catalog = models.BooleanField(null=True)
    fetch_timed_out = False
    course_registration_message = models.CharField(max_length=255, blank=True, default='')
    on_site_exams_info = JSONField(null=True)

    def _get_academic_year_template_formated(self):
        return '{} - {}'.format(self.academic_year, self.academic_year + 1)

    academic_year_template_formated = property(_get_academic_year_template_formated)

    class Meta:
        unique_together = ('registration_id', 'academic_year', 'acronym')

    def __str__(self):
        return '{} - {} - {}'.format(self.registration_id, self.acronym, self.academic_year)


def search(registration_id=None, academic_year=None, acronym=None):
    """
        Search students by optional arguments. At least one argument should be informed
        otherwise it returns empty.
    """
    has_criteria = False
    student_performances = StudentPerformance.objects.all()
    if registration_id:
        student_performances = student_performances.filter(registration_id=registration_id)
        has_criteria = True
    if academic_year:
        student_performances = student_performances.filter(academic_year=academic_year)
        has_criteria = True
    if acronym:
        student_performances = student_performances.filter(acronym=acronym)
        has_criteria = True

    if has_criteria:
        return student_performances.order_by('-academic_year')
    else:
        return None


def update_or_create(registration_id, academic_year, acronym, fields):
    obj, created = StudentPerformance.objects.update_or_create(registration_id=registration_id,
                                                               academic_year=academic_year,
                                                               acronym=acronym,
                                                               defaults=fields)
    return obj


def find_actual_by_student_and_offer_year(registration_id, academic_year, acronym):
    try:
        result = StudentPerformance.objects.get(registration_id=registration_id,
                                                academic_year=academic_year,
                                                acronym=acronym)
    except ObjectDoesNotExist:
        result = None
    if result and has_expired(result):
        new_result = fetch_and_save(result.registration_id, result.academic_year, result.acronym)
        if new_result:
            result = new_result
        else:
            result.fetch_timed_out = True
    return result


def has_expired(student_performance):
    now = timezone.now()
    expiration_date = student_performance.update_date
    return expiration_date < now


def find_actual_by_pk(student_performance_pk):
    result = find_by_pk(student_performance_pk)
    if result and has_expired(result):
        new_result = fetch_and_save(result.registration_id, result.academic_year, result.acronym)
        if new_result:
            result = new_result
        else:
            result.fetch_timed_out = True
    return result


def find_by_pk(student_performance_pk):
    try:
        result = StudentPerformance.objects.get(pk=student_performance_pk)
    except ObjectDoesNotExist:
        result = None
    return result


def find_by_acronym_and_academic_year(acronym, academic_year):
    return StudentPerformance.objects.filter(acronym=acronym, academic_year=academic_year)
