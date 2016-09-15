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


class ApplicationAssimilationCriteriaAdmin(admin.ModelAdmin):
    list_display = ('application', 'criteria', 'selected')


class ApplicationAssimilationCriteria(models.Model):
    application = models.ForeignKey('Application')
    criteria = models.ForeignKey('reference.AssimilationCriteria')
    additional_criteria = models.ForeignKey('reference.AssimilationCriteria', blank=True, null=True,
                                            related_name='application_additional_criteria')
    selected = models.NullBooleanField(null=True, blank=True)


def find_by_application(application):
    return ApplicationAssimilationCriteria.objects.filter(application=application)


def find_by_criteria(criteria):
    return ApplicationAssimilationCriteria.objects.get(criteria=criteria)


def search(application=None, criteria=None):
    out = None
    queryset = ApplicationAssimilationCriteria.objects
    if application:
        queryset = queryset.filter(application=application)
    if criteria:
        queryset = queryset.filter(criteria=criteria)
    if application or criteria:
        out = queryset
    return out


def find_first(application=None, criteria=None):
    results = search(application, criteria)
    if results.exists():
        return results[0]
    return None


def copy_from_applicant_assimilation_criteria(applicant_assimilation_criteria, application):
    application_assimilation_criteria = ApplicationAssimilationCriteria()
    application_assimilation_criteria.application = application
    application_assimilation_criteria.criteria = applicant_assimilation_criteria.criteria
    if applicant_assimilation_criteria.additional_criteria:
        application_assimilation_criteria.additional_criteria = \
            applicant_assimilation_criteria.additional_criteria
    else:
        applicant_assimilation_criteria.additional_criteria = None
    application_assimilation_criteria.selected = applicant_assimilation_criteria.selected
    application_assimilation_criteria.save()
