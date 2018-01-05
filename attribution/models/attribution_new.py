##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2017 Université catholique de Louvain (http://www.uclouvain.be)
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
from decimal import Decimal
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.contrib import admin


class AttributionNewAdmin(admin.ModelAdmin):
    list_display = ('global_id', 'attributions', 'applications')
    fieldsets = ((None, {'fields': ('global_id', 'attributions', 'applications', 'summary_responsible' )}),)
    search_fields = ['global_id']
    list_filter = ('summary_responsible', )


class AttributionNew(models.Model):
    global_id = models.CharField(max_length=10, unique=True)
    attributions = JSONField(default=list, blank=True)
    applications = JSONField(default=list, blank=True)
    summary_responsible = models.BooleanField(default=False)

    class Meta:
        permissions = (
            ("can_access_attribution_application", "Can access attribution application"),
        )

    def __str__(self):
        return u"%s" % self.global_id

    def save(self, *args, **kwargs):
        if self.attributions and isinstance(self.attributions, list):
            self.attributions = _convert_decimal_to_str(self.attributions)
        if self.applications and isinstance(self.applications, list):
            self.applications = _convert_decimal_to_str(self.applications)
        super(AttributionNew, self).save(*args, **kwargs)


def _convert_decimal_to_str(item_list):
    for item in item_list:
        for key in item.keys():
            if isinstance(item[key], Decimal):
                item[key] = str(item[key])
    return item_list


def insert_or_update_attributions(global_id, attributions_data):
    AttributionNew.objects.update_or_create(
        global_id=global_id, defaults={"attributions": attributions_data}
    )


def find_by_global_id(global_id):
    try:
        return AttributionNew.objects.get(global_id=global_id)
    except AttributionNew.DoesNotExist:
        return None


def find_teachers(an_acronym, yr):
    return AttributionNew.objects.filter(attributions__contains=[{'acronym': an_acronym,
                                                                  'year': yr}])
