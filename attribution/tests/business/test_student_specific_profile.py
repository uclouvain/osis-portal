##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2022 Université catholique de Louvain (http://www.uclouvain.be)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################

from django.test import TestCase
from django.utils.translation import gettext as _
from osis_learning_unit_enrollment_sdk.model.student_specific_profile import StudentSpecificProfile
from osis_learning_unit_enrollment_sdk.model.subtype_enum import SubtypeEnum
from osis_learning_unit_enrollment_sdk.model.type_peps_enum import TypePepsEnum

from attribution.business.student_specific_profile import get_type_peps, get_guide, get_arrangements


class StudentSpecificProfileTest(TestCase):
    def setUp(self):
        self.guide = "John Doe"
        self.student_specific_profile = StudentSpecificProfile(**{
            'type': TypePepsEnum("SPORT"),
            'type_text': "Type SPORT",
            'subtype': SubtypeEnum("PROMISING_ATHLETE_HL"),
            'subtype_text': "Subtype ATHLETE",
            'guide': self.guide,
            'arrangement_additional_time': "time",
            'arrangement_appropriate_copy': "copy",
            'arrangement_specific_locale': True,
            'arrangement_exam_comment': "exam",
            'arrangement_course_comment': "course",
            'arrangement_internship_comment': "internship",
            'arrangement_dissertation_comment': "dissertation",
            'arrangement_comment': "comment",
        })

    def test_get_type_peps_sport(self):
        sport_peps = get_type_peps(student_specific_profile=self.student_specific_profile)
        self.assertEqual(sport_peps, "{} - {}".format(
            self.student_specific_profile.type_text,
            self.student_specific_profile.subtype_text
        ))

    def test_get_type_peps_disability(self):
        disability_type_text = "Disability"
        disability_subtype_text = "Disability subtype"

        self.student_specific_profile.type = TypePepsEnum("DISABILITY")
        self.student_specific_profile.type_text = disability_type_text
        self.student_specific_profile.subtype_text = disability_subtype_text

        disability_peps = get_type_peps(student_specific_profile=self.student_specific_profile)
        self.assertEqual(disability_peps, "{} - {}".format(disability_type_text, disability_subtype_text))

    def test_get_type_peps_not_defined(self):

        self.student_specific_profile.type = TypePepsEnum("NOT_DEFINED")

        not_defined_peps = get_type_peps(student_specific_profile=self.student_specific_profile)
        self.assertEqual(not_defined_peps, "-")

    def test_get_guide(self):
        guide = get_guide(student_specific_profile=self.student_specific_profile)
        self.assertEqual(guide, self.guide)

    def test_get_arrangements(self):
        arrangements = get_arrangements(spec_profile=self.student_specific_profile)
        expected_result = [
            _('Extra time (33% generally)'),
            _('Large print'),
            _('Specific room of examination'),
            _('Other educational facilities'),
            "{} : {}".format(_('For exam'), 'exam'),
            "{} : {}".format(_('For course'), 'course'),
            "{} : {}".format(_('For internship'), 'internship'),
            "{} : {}".format(_('For dissertation'), 'dissertation'),
        ]
        self.assertEqual(arrangements, expected_result)
