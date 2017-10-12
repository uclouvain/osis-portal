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
from osis_common.models.serializable_model import SerializableModel, SerializableModelAdmin
from dissertation.models.offer_proposition_group import OfferPropositionGroup
from django.db import models
from django.utils import timezone
from base.models import offer


class OfferPropositionAdmin(SerializableModelAdmin):
    list_display = ('acronym', 'offer')
    raw_id_fields = ('offer',)
    search_fields = ('uuid',)


class OfferProposition(SerializableModel):
    acronym = models.CharField(max_length=200)
    offer = models.ForeignKey(offer.Offer)
    student_can_manage_readers = models.BooleanField(default=True)
    adviser_can_suggest_reader = models.BooleanField(default=False)
    evaluation_first_year = models.BooleanField(default=False)
    validation_commission_exists = models.BooleanField(default=False)
    start_visibility_proposition = models.DateField(default=timezone.now)
    end_visibility_proposition = models.DateField(default=timezone.now)
    start_visibility_dissertation = models.DateField(default=timezone.now)
    end_visibility_dissertation = models.DateField(default=timezone.now)
    start_jury_visibility = models.DateField(default=timezone.now)
    end_jury_visibility = models.DateField(default=timezone.now)
    start_edit_title = models.DateField(default=timezone.now)
    end_edit_title = models.DateField(default=timezone.now)
    offer_proposition_group = models.ForeignKey(OfferPropositionGroup, null=True, blank=True)

    def __str__(self):
        return self.acronym


def get_all_offers():
    offer_propositions = list(OfferProposition.objects.all().select_related('offer'))
    return [obj.offer for obj in offer_propositions]


def search_by_offer(off):
    return OfferProposition.objects.get(offer=off)


def search_by_offers(offers):
    return OfferProposition.objects.filter(offer__in=offers)
