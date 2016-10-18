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
"""
Model containing a profession.
This can be executive, artist, worker and so on.
"""
from django.db import models


class Profession(models.Model):
    name = models.CharField(max_length=255)
    adhoc = models.BooleanField(default=False)

    def __str__(self):
        return u"%s" % self.name


def find_by_id(an_id):
    try:
        return Profession.objects.get(pk=an_id)
    except:
        return None


def find_by_adoc(an_adhoc):
    return Profession.objects.filter(adhoc=an_adhoc).order_by('name')

def find_by_name(a_name):
    return Profession.objects.filter(name=a_name).first()