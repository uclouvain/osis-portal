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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
from django.test import TestCase

from base.models.signals import _add_person_to_group, GROUP_STUDENTS_INTERNSHIP
from base.tests.factories.person import PersonFactory
from base.tests.models.test_signals import get_or_create_user
from internship.tests.factories.internship_student_information import InternshipStudentInformationFactory


class UpdatePersonIfNecessary(TestCase):

    user_infos = {
        'USERNAME': 'user_test',
        'PASSWORD': 'pass_test',
        'USER_FGS': '22222222',
        'USER_FIRST_NAME': 'user_first',
        'USER_LAST_NAME': 'user_last',
        'USER_EMAIL': 'user1@user.org'
    }

    def test_when_internship_installed(self):
        user = get_or_create_user(self.user_infos)
        person = PersonFactory(
            user=user,
            first_name="user3",
            last_name="user3",
            email='test3@test.org',
            global_id="1111111"
        )
        InternshipStudentInformationFactory(person=person)
        _add_person_to_group(person)
        self.assertTrue(person.user.groups.filter(name=GROUP_STUDENTS_INTERNSHIP).exists())
