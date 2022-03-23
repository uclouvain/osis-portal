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
from typing import List

from django.utils.translation import ugettext as _
from osis_learning_unit_enrollment_sdk.model.student_specific_profile import StudentSpecificProfile

from base.models.enums import peps_type


def get_type_peps(student_specific_profile: StudentSpecificProfile) -> str:
    if student_specific_profile.type.value in [peps_type.PepsTypes.SPORT.name, peps_type.PepsTypes.DISABILITY.name]:
        return "{} - {}".format(student_specific_profile.type_text, student_specific_profile.subtype_text)
    if student_specific_profile.type.value == peps_type.PepsTypes.NOT_DEFINED.name:
        return "-"
    return student_specific_profile.type_text or "-"


def get_arrangements(spec_profile: StudentSpecificProfile) -> List[str]:
    arrangements = []
    if spec_profile.arrangement_additional_time:
        arrangements.append(_('Extra time (33% generally)'))
    if spec_profile.arrangement_appropriate_copy:
        arrangements.append(_('Large print'))
    if spec_profile.arrangement_specific_locale:
        arrangements.append(_('Specific room of examination'))
    if _has_other_facility_comment(spec_profile):
        arrangements.append(_('Other educational facilities'))
        if spec_profile.arrangement_exam_comment:
            arrangements.append("{} : {}".format(_('For exam'), spec_profile.arrangement_exam_comment))
        if spec_profile.arrangement_course_comment:
            arrangements.append("{} : {}".format(_('For course'), spec_profile.arrangement_course_comment))
        if spec_profile.arrangement_internship_comment:
            arrangements.append("{} : {}".format(_('For internship'), spec_profile.arrangement_internship_comment))
        if spec_profile.arrangement_dissertation_comment:
            arrangements.append("{} : {}".format(_('For dissertation'), spec_profile.arrangement_dissertation_comment))

    return arrangements


def get_guide(student_specific_profile) -> str:
    return str(student_specific_profile.guide) if student_specific_profile.guide else None


def _has_other_facility_comment(student_specific_profile):
    return any(
        [
            student_specific_profile.arrangement_exam_comment,
            student_specific_profile.arrangement_course_comment,
            student_specific_profile.arrangement_internship_comment,
            student_specific_profile.arrangement_dissertation_comment,
        ]
    )
