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
from admission.models import form
from admission.models.enums import question_type
from osis_common.models.serializable_model import SerializableModel


class QuestionAdmin(admin.ModelAdmin):
    list_display = ('label', 'type', 'form', 'order')
    fieldsets = ((None, {'fields': ('label', 'description', 'type', 'order', 'required', 'form')}),)
    list_filter = ('form',)
    raw_id_fields = ('form',)
    search_fields = ['form']


class Question(SerializableModel):
    label = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    type = models.CharField(max_length=20, choices=question_type.QUESTION_TYPES)
    order = models.IntegerField(blank=True, null=True)
    required = models.BooleanField(default=False)
    form = models.ForeignKey('Form')

    def __str__(self):
        return u"%s" % self.label


def find_form_ordered_questions(offer_year):
    form_offer_yr = form.Form.objects.filter(offer_year=offer_year)
    if form_offer_yr:
        return Question.objects.filter(form=form_offer_yr).order_by("order")
    return None
