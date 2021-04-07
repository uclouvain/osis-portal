##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2021 Université catholique de Louvain (http://www.uclouvain.be)
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
from django.utils.translation import gettext_lazy as _

from osis_common.utils.enumerations import ChoiceEnum


class Civility(ChoiceEnum):
    PROFESSOR = "PROFESSOR"
    DOCTOR = "DOCTOR"

    @classmethod
    def get_acronym(cls, civility):
        if civility == cls.PROFESSOR.value:
            return "Prof."
        elif civility == cls.DOCTOR.value:
            return "Dr."

    @classmethod
    def choices(cls):
        return tuple((x.value, _(x.value)) for x in cls)
