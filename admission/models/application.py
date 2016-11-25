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
from django.core.exceptions import ObjectDoesNotExist
from admission.models import applicant
from localflavor.generic.models import IBANField, BICField
from localflavor.generic.countries.sepa import IBAN_SEPA_COUNTRIES
from admission.models.enums import application_type, coverage_access_degree


class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('applicant', 'offer_year', 'creation_date', 'application_type')
    fieldsets = ((None, {'fields': ('applicant', 'offer_year', 'application_type', 'applied_to_sameprogram',
                                    'coverage_access_degree', 'valuation_possible')}),)


class Application(models.Model):

    applicant = models.ForeignKey('Applicant')
    offer_year = models.ForeignKey('base.OfferYear')
    creation_date = models.DateTimeField(auto_now=True)
    application_type = models.CharField(max_length=20, choices=application_type.APPLICATION_TYPE_CHOICES)
    coverage_access_degree = models.CharField(max_length=30, blank=True, null=True,
                                              choices=coverage_access_degree.COVERAGE_ACCESS_DEGREE_CHOICES)
    valuation_possible = models.NullBooleanField(default=None)
    started_similar_studies = models.NullBooleanField(default=None)
    credits_to_value = models.NullBooleanField(default=None)
    applied_to_sameprogram = models.NullBooleanField(default=None)
    resident = models.NullBooleanField(default=None)
    raffle_number = models.CharField(max_length=50, blank=True, null=True)
    study_grant = models.BooleanField(default=False)
    study_grant_number = models.CharField(max_length=50, blank=True, null=True)
    deduction_children = models.BooleanField(default=False)
    scholarship = models.BooleanField(default=False)
    scholarship_organization = models.TextField(blank=True, null=True)
    sport_membership = models.BooleanField(default=False)
    culture_membership = models.BooleanField(default=False)
    solidarity_membership = models.BooleanField(default=False)
    bank_account_iban = IBANField(include_countries=IBAN_SEPA_COUNTRIES, blank=True, null=True)
    bank_account_bic = BICField(blank=True, null=True)
    bank_account_name = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return u"%s %s" % (self.applicant, self.offer_year)


def find_by_user(user):
    try:
        an_applicant = applicant.Applicant.objects.get(user=user)

        if an_applicant:
            return Application.objects.filter(applicant=an_applicant)
        else:
            return None
    except ObjectDoesNotExist:
        return None


def find_by_id(application_id):
    return Application.objects.get(pk=application_id)


def find_first_by_user(user):
    try:
        an_applicant = applicant.Applicant.objects.get(user=user)

        if an_applicant:
            return Application.objects.filter(applicant=an_applicant).first()
        else:
            return None
    except ObjectDoesNotExist:
        return None


def init_application(user):
    an_applicant = applicant.Applicant.objects.get(user=user)
    application = Application()
    application.applicant = an_applicant
    return application


def define_application_type(a_coverage_access_degree, user):
    an_applicant = applicant.Applicant.objects.get(user=user)

    if an_applicant.nationality and \
            an_applicant.nationality.european_union and \
                    a_coverage_access_degree == coverage_access_degree.NATIONAL:
        return application_type.INSCRIPTION
    return application_type.ADMISSION

