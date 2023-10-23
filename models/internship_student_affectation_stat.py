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

from internship.models.enums.affectation_type import AffectationType
from internship.models.enums.choice_type import ChoiceType
from osis_common.models.serializable_model import SerializableModel


class InternshipStudentAffectationStat(SerializableModel):
    student = models.ForeignKey('base.Student', on_delete=models.PROTECT)
    speciality = models.ForeignKey('internship.InternshipSpeciality', on_delete=models.CASCADE)
    choice = models.CharField(max_length=1, choices=ChoiceType.choices(), default=ChoiceType.NO_CHOICE.value)
    cost = models.IntegerField(blank=False, null=False)
    consecutive_month = models.BooleanField(default=False, null=False)
    type = models.CharField(max_length=1, choices=AffectationType.choices(), default=AffectationType.NORMAL.value)


def search(student=None):
    return InternshipStudentAffectationStat.objects.filter(student=student).order_by('period__date_start')
