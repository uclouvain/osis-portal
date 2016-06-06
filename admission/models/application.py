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
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ObjectDoesNotExist
from admission.models import person


class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('person', 'offer_year', 'creation_date', 'application_type', 'doctorate')
    fieldsets = ((None, {'fields': ('person', 'offer_year', 'application_type', 'doctorate')}),)


class Application(models.Model):
    APPLICATION_TYPE = (('ADMISSION', _('admission')),
                        ('INSCRIPTION', _('inscription')))

    person = models.ForeignKey('Person')
    offer_year = models.ForeignKey('OfferYear')
    creation_date = models.DateTimeField(auto_now=True)
    application_type = models.CharField(max_length=20, choices=APPLICATION_TYPE)
    doctorate = models.BooleanField(default=False)
    belgian_degree = models.NullBooleanField(default=None)
    vae = models.NullBooleanField(default=None)
    started_samestudies = models.NullBooleanField(default=None)
    credits_to_value = models.NullBooleanField(default=None)
    applied_to_sameprogram = models.NullBooleanField(default=None)
    resident = models.NullBooleanField(default=None)
    lottery_number = models.CharField(max_length=50, blank=True, null=True)
    study_grant = models.BooleanField(default=False)
    study_grant_number = models.CharField(max_length=50, blank=True, null=True)
    deduction_children = models.BooleanField(default=False)
    scholarship = models.BooleanField(default=False)
    scholarship_organization = models.TextField(blank=True, null=True)
    sport_membership = models.BooleanField(default=False)
    culture_membership = models.BooleanField(default=False)
    solidary_membership = models.BooleanField(default=False)
    bank_account_iban = models.CharField(max_length=50, blank=True, null=True)
    bank_account_bic = models.CharField(max_length=50, blank=True, null=True)
    bank_account_name = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return u"%s" % self.offer_year


def find_by_user(user):
    try:
        person_application = person.Person.objects.get(user=user)

        if person_application:
            return Application.objects.filter(person=person_application)
        else:
            return None
    except ObjectDoesNotExist:
        return None


def find_by_id(application_id):
    return Application.objects.get(pk=application_id)


def find_first_by_user(user):
    try:
        person_application = person.Person.objects.get(user=user)

        if person_application:
            return Application.objects.filter(person=person_application).first()
        else:
            return None
    except ObjectDoesNotExist:
        return None