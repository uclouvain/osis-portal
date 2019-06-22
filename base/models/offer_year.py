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


class OfferYearAdmin(SerializableModelAdmin):
    list_display = ('acronym', 'title', 'academic_year', 'grade_type', 'enrollment_enabled')
    list_filter = ('grade_type__institutional_grade_type', 'enrollment_enabled')
    fieldsets = ((None, {'fields': ('academic_year', 'acronym', 'title', 'title_international', 'grade_type',
                                    'offer', 'enrollment_enabled')}),)
    search_fields = ['acronym']
    raw_id_fields = ('offer',)


class OfferYear(SerializableModel):
    external_id = models.CharField(max_length=100, blank=True, null=True)
    academic_year = models.ForeignKey('base.AcademicYear')
    acronym = models.CharField(max_length=15)
    title = models.CharField(max_length=255)
    title_international = models.CharField(max_length=255, blank=True, null=True)
    grade_type = models.ForeignKey('reference.GradeType', blank=True, null=True, db_index=True)
    offer = models.ForeignKey('base.Offer', blank=True, null=True)
    campus = models.ForeignKey('base.Campus', blank=True, null=True)
    enrollment_enabled = models.BooleanField(default=False)

    def __str__(self):
        return u"%s - %s" % (self.academic_year, self.acronym)


def find_by_id(offer_year_id):
    return OfferYear.objects.get(pk=offer_year_id)


def find_by_domain_grade(domain, grade):
    return OfferYear.objects.filter(domain=domain, grade_type=grade).order_by("acronym")


def find_by_offer(offers):
    return OfferYear.objects.filter(offer__in=offers)


def find_by_student(student):
    return OfferYear.objects.filter(offerenrollment__student=student).order_by("academic_year__year", "acronym")


def find_by_student_and_offers(student, offers):
    return find_by_student(student).filter(offer__in=offers)


def find_by_acronym_and_year(acronym, year):
    return OfferYear.objects.filter(acronym=acronym, academic_year__year=year).order_by('acronym').first()
