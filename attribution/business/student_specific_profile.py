##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2020 Université catholique de Louvain (http://www.uclouvain.be)
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
from base.models.enums import peps_type
from base.models.student_specific_profile import StudentSpecificProfile
from django.utils.translation import ugettext as _


def get_type_peps(student_specific_profile: StudentSpecificProfile) -> str:
    if student_specific_profile.type == peps_type.PepsTypes.SPORT.name:
        return "{} - {}".format(
            str(_(student_specific_profile.get_type_display())) or "-",
            str(_(student_specific_profile.get_subtype_sport_display())) or "-",
        )
    if student_specific_profile.type == peps_type.PepsTypes.DISABILITY.name:
        return "{} - {}".format(
            str(_(student_specific_profile.get_type_display())) or "-",
            str(_(student_specific_profile.get_subtype_disability_display())) or "-",
        )

    return str(_(student_specific_profile.get_type_display())) or "-"
