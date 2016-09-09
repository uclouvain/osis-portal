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


class ApplicantAssimilationCriteriaAdmin(admin.ModelAdmin):
    list_display = ('applicant', 'criteria')


class ApplicantAssimilationCriteria(models.Model):
    applicant = models.ForeignKey('Applicant')
    criteria = models.ForeignKey('reference.AssimilationCriteria')


def find_by_applicant(applicant):
    return ApplicantAssimilationCriteria.objects.filter(applicant=applicant)


def find_by_criteria(criteria):
    return ApplicantAssimilationCriteria.objects.get(criteria=criteria)


def search(applicant=None, criteria=None):
    out = None
    queryset = ApplicantAssimilationCriteria.objects
    if applicant:
        queryset = queryset.filter(applicant=applicant)
    if criteria:
        queryset = queryset.filter(criteria=criteria)
    if applicant or criteria:
        out = queryset
    return out
