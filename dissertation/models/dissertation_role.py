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
from osis_common.models.serializable_model import SerializableModel
from django.contrib import admin
from django.db import models
from django.utils.translation import ugettext_lazy as _


class DissertationRoleAdmin(admin.ModelAdmin):
    list_display = ('adviser', 'status', 'dissertation', 'author', 'dissertation_status')


class DissertationRole(SerializableModel):
    STATUS_CHOICES = (
        ('PROMOTEUR', _('promotor')),
        ('CO_PROMOTEUR', _('copromotor')),
        ('READER', _('reader')),
    )

    status = models.CharField(max_length=12, choices=STATUS_CHOICES)
    adviser = models.ForeignKey('Adviser')
    dissertation = models.ForeignKey('Dissertation')

    def __str__(self):
        return u"%s %s" % (self.status if self.status else "", self.adviser if self.adviser else "")

    @property
    def author(self):
        return self.dissertation.author

    @property
    def dissertation_status(self):
        return self.dissertation.status


def add(status, adviser, dissertation):
    if count_by_status_student_dissertation(status, adviser, dissertation) == 0:
        role = DissertationRole(status=status, adviser=adviser, dissertation=dissertation)
        role.save()


def count_by_dissertation(dissertation):
    return DissertationRole.objects.filter(dissertation=dissertation).count()


def count_reader_by_dissertation(dissertation):
    return DissertationRole.objects.filter(dissertation=dissertation, status="READER").count()


def count_by_status_student_dissertation(status, adviser, dissertation):
    return DissertationRole.objects.filter(adviser=adviser)\
        .filter(status=status)\
        .filter(dissertation=dissertation)\
        .count()


def get_promoteur_by_dissertation(dissertation):
    promoteur = search_by_dissertation_and_role(dissertation, 'PROMOTEUR')
    return promoteur


def search_by_dissertation(dissertation):
    return DissertationRole.objects.filter(dissertation=dissertation)


def search_by_dissertation_and_role(dissertation, role):
    dissertation_role = search_by_dissertation(dissertation).get(status=role)
    return dissertation_role.adviser
