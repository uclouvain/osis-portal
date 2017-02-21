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
from dissertation.models import proposition_offer
from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _


class PropositionDissertationAdmin(SerializableModelAdmin):
    list_display = ('title', 'author', 'visibility', 'active', 'creator')
    raw_id_fields = ('creator', 'author')
    search_fields = ('uuid', 'title', 'author__person__last_name', 'author__person__first_name')


class PropositionDissertation(SerializableModel):
    TYPES_CHOICES = (
        ('RDL', _('litterature_review')),
        ('EMP', _('empirical_research')),
        ('THE', _('theoretical_analysis')),
        ('PRO', _('project_dissertation')),
        ('DEV', _('development_dissertation')),
        ('OTH', _('other')))

    LEVELS_CHOICES = (
        ('SPECIFIC', _('specific_subject')),
        ('THEME', _('large_theme')))

    COLLABORATION_CHOICES = (
        ('POSSIBLE', _('possible')),
        ('REQUIRED', _('required')),
        ('FORBIDDEN', _('forbidden')))

    author = models.ForeignKey('Adviser')
    creator = models.ForeignKey('base.Person', blank=True, null=True)
    collaboration = models.CharField(max_length=12, choices=COLLABORATION_CHOICES, default='FORBIDDEN')
    description = models.TextField(blank=True, null=True)
    level = models.CharField(max_length=12, choices=LEVELS_CHOICES, default='DOMAIN')
    max_number_student = models.IntegerField()
    title = models.CharField(max_length=200)
    type = models.CharField(max_length=12, choices=TYPES_CHOICES, default='RDL')
    visibility = models.BooleanField(default=True)
    active = models.BooleanField(default=True)
    created_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        first_name = ""
        middle_name = ""
        last_name = ""
        if self.author.person.first_name:
            first_name = self.author.person.first_name
        if self.author.person.middle_name:
            middle_name = self.author.person.middle_name
        if self.author.person.last_name:
            last_name = self.author.person.last_name + ","
        author = u"%s %s %s" % (last_name.upper(), first_name, middle_name)
        return author+" - "+str(self.title)

    class Meta:
        ordering = ["author__person__last_name", "author__person__middle_name", "author__person__first_name", "title"]


def search(terms, active=None, visibility=None):
    queryset = PropositionDissertation.objects.all()
    if terms:
        queryset = queryset.filter(
            Q(title__icontains=terms) |
            Q(description__icontains=terms) |
            Q(author__person__first_name__icontains=terms) |
            Q(author__person__middle_name__icontains=terms) |
            Q(author__person__last_name__icontains=terms)
        )
    if active:
        queryset = queryset.filter(active=active)
    elif visibility:
        queryset = queryset.filter(visibility=visibility)
    queryset = queryset.distinct()
    return queryset


def find_by_id(proposition_id):
    return PropositionDissertation.objects.get(pk=proposition_id)


def search_by_offers(offers):
    proposition_ids = proposition_offer.find_by_offers(offers).values('proposition_dissertation_id')
    return PropositionDissertation.objects.filter(pk__in=proposition_ids, active=True, visibility=True)
