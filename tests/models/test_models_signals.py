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
from django.contrib.auth.models import User, Group
from django.test import TestCase

from base.models.person import Person
from base.models.signals import GROUP_STUDENTS_INTERNSHIP
from internship.models.internship_student_information import InternshipStudentInformation
from internship.tests.factories.cohort import CohortFactory


class AddToGroupsSignalsTest(TestCase):

    def setUp(self):
        self.user_foo = User.objects.create_user('user_foo')
        self.person_foo = Person.objects.create(user=self.user_foo)
        Group.objects.get_or_create(name=GROUP_STUDENTS_INTERNSHIP)

    def create_internships_student_foo(self):
        cohort = CohortFactory()
        return InternshipStudentInformation.objects.create(person=self.person_foo, cohort=cohort,
                                                           location='Location',
                                                           postal_code='postal_code',
                                                           city='city',
                                                           country='country')

    def is_member(self, group):
        return self.user_foo.groups.filter(name=group).exists()

    def test_add_to_internship_students_group(self):
        self.create_internships_student_foo()
        self.assertTrue(self.is_member('internship_students'), 'user_foo should be in internship_students group')

    def test_remove_from_internship_students_group(self):
        internship_student = self.create_internships_student_foo()
        internship_student.delete()
        self.assertFalse(self.is_member('internship_students'), 'user_foo should not be in internship_students group')
