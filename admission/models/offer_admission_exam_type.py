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
from admission.models.enums import application_type


class OfferAdmissionExamTypeAdmin(admin.ModelAdmin):
    list_display = ('offer_year', 'admission_exam_type')
    fieldsets = ((None, {'fields': ('offer_year', 'admission_exam_type')}),)
    list_filter = ('offer_year',)


class OfferAdmissionExamType(models.Model):

    offer_year = models.ForeignKey('base.OfferYear', null=False)
    admission_exam_type = models.ForeignKey('AdmissionExamType', null=False)


def find_by_offer_year(an_offer_year):
    return OfferAdmissionExamType.objects.filter(offer_year=an_offer_year).first()