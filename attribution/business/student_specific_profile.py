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
from learning_unit.services.learning_unit import LearningUnitTypeEnum


def get_type_peps(student_specific_profile: StudentSpecificProfile) -> str:
    if student_specific_profile.type.value in [peps_type.PepsTypes.SPORT.name, peps_type.PepsTypes.DISABILITY.name]:
        return f"{student_specific_profile.type_text} - {student_specific_profile.subtype_text}"

    if student_specific_profile.type.value == peps_type.PepsTypes.NOT_DEFINED.name:
        return "-"
    return student_specific_profile.type_text or "-"


def get_arrangements(spec_profile: StudentSpecificProfile, learning_unit_type: str) -> List[str]:
    arrangements = []
    if is_type_course_or_others(learning_unit_type):
        if spec_profile.arrangement_additional_time.value:
            arrangements.append(spec_profile.arrangement_additional_time_text)
        if spec_profile.arrangement_appropriate_copy.value:
            arrangements.append(f"{_('Copy')} : {spec_profile.arrangement_appropriate_copy_text}")

        if spec_profile.arrangement_specific_locale:
            arrangements.append(_('Specific room of examination'))
    if _has_other_facility_comment(spec_profile, learning_unit_type):
        arrangements.append(_('Other educational facilities : see Excel'))

    return arrangements


def get_guide(student_specific_profile) -> str:
    return str(student_specific_profile.guide) if student_specific_profile.guide else None


def _has_other_facility_comment(student_specific_profile, learning_unit_type: str) -> bool:
    return _has_comments_related_to_course_and_others(learning_unit_type, student_specific_profile) or \
           _has_comments_related_to_internship(learning_unit_type, student_specific_profile) or \
           _has_comments_related_to_dissertation(learning_unit_type, student_specific_profile)


def _has_comments_related_to_dissertation(learning_unit_type, student_specific_profile):
    return learning_unit_type == LearningUnitTypeEnum.DISSERTATION.value \
           and student_specific_profile.arrangement_dissertation_comment


def _has_comments_related_to_internship(learning_unit_type, student_specific_profile):
    return learning_unit_type == LearningUnitTypeEnum.INTERNSHIP.value \
           and student_specific_profile.arrangement_internship_comment


def _has_comments_related_to_course_and_others(learning_unit_type, student_specific_profile):
    return is_type_course_or_others(learning_unit_type) and any([
        student_specific_profile.arrangement_exam_comment,
        student_specific_profile.arrangement_course_comment,
        student_specific_profile.arrangement_exam,
        student_specific_profile.arrangement_course
    ])


def is_type_course_or_others(learning_unit_type):
    return learning_unit_type in [
        LearningUnitTypeEnum.COURSE.value,
        LearningUnitTypeEnum.OTHER_INDIVIDUAL.value,
        LearningUnitTypeEnum.OTHER_COLLECTIVE.value
    ]
