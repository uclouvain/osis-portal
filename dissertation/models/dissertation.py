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

from django.contrib import admin
from django.db import models
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from base.models import student, offer_year, academic_year
from . import dissertation_location, proposition_dissertation
from dissertation.models.dissertation_role import get_promoteur_by_dissertation
from dissertation.utils.emails_dissert import send_mail_to_teacher_new_dissert


class DissertationAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'status', 'active')


STATUS_CHOICES = (
    ('DRAFT', _('draft')),
    ('DIR_SUBMIT', _('submitted_to_director')),
    ('DIR_OK', _('accepted_by_director')),
    ('DIR_KO', _('refused_by_director')),
    ('COM_SUBMIT', _('submitted_to_commission')),
    ('COM_OK', _('accepted_by_commission')),
    ('COM_KO', _('refused_by_commission')),
    ('EVA_SUBMIT', _('submitted_to_first_year_evaluation')),
    ('EVA_OK', _('accepted_by_first_year_evaluation')),
    ('EVA_KO', _('refused_by_first_year_evaluation')),
    ('TO_RECEIVE', _('to_be_received')),
    ('TO_DEFEND', _('to_be_defended')),
    ('DEFENDED', _('defended')),
    ('ENDED', _('ended')),
    ('ENDED_WIN', _('ended_win')),
    ('ENDED_LOS', _('ended_los')),
)

DEFEND_PERIODE_CHOICES = (
    ('UNDEFINED', _('undefined')),
    ('JANUARY', _('january')),
    ('JUNE', _('june')),
    ('SEPTEMBER', _('september')),
)


class Dissertation(models.Model):

    title = models.CharField(max_length=200)
    author = models.ForeignKey(student.Student)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='DRAFT')
    defend_periode = models.CharField(max_length=12, choices=DEFEND_PERIODE_CHOICES, default='UNDEFINED')
    defend_year = models.ForeignKey(academic_year.AcademicYear, blank=True, null=True)
    offer_year_start = models.ForeignKey(offer_year.OfferYear)
    proposition_dissertation = models.ForeignKey(proposition_dissertation.PropositionDissertation)
    description = models.TextField(blank=True, null=True)
    active = models.BooleanField(default=True)
    creation_date = models.DateTimeField(auto_now_add=True, editable=False)
    modification_date = models.DateTimeField(auto_now=True)
    location = models.ForeignKey(dissertation_location.DissertationLocation, blank=True, null=True)

    def __str__(self):
        return self.title

    def deactivate(self):
        self.active = False
        self.save()

    def set_status(self, status):
        self.status = status
        self.save()

    def go_forward(self):
        next_status = get_next_status(self, "go_forward")
        if self.status == 'DRAFT' and next_status == 'DIR_SUBMIT':
            send_mail_to_teacher_new_dissert(get_promoteur_by_dissertation(self))
        self.set_status(next_status)

    def accept(self):
        next_status = get_next_status(self, "accept")
        self.set_status(next_status)

    def refuse(self):
        next_status = get_next_status(self, "refuse")
        self.set_status(next_status)


def count_by_proposition(subject):
    return Dissertation.objects.filter(active=True)\
                               .filter(proposition_dissertation=subject)\
                               .exclude(status='DRAFT')\
                               .count()


def count_submit_by_user(user, offer):
    return Dissertation.objects.filter(author=user).filter(offer_year_start__offer=offer)\
        .exclude(status='DRAFT').exclude(status='DIR_KO').count()


def get_next_status(memory, operation):
    if operation == "go_forward":
        if memory.status == 'DRAFT' or memory.status == 'DIR_KO':
            return 'DIR_SUBMIT'
        else:
            return memory.status
    else:
        return memory.status


def search(terms, author=None):
    queryset = Dissertation.objects.all()
    if terms:
        queryset = queryset.filter(
            Q(title__icontains=terms) |
            Q(description__icontains=terms)
        )
    queryset = queryset.filter(author=author)
    queryset = queryset.distinct()
    return queryset


def search_by_user(user):
    return Dissertation.objects.filter(author=user).exclude(active=False)
