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
from django.contrib.auth.models import User, Group
from django.test import TestCase

from base.models import signals
from base.models.tutor import Tutor
from base.tests.factories.person import PersonFactory




class TestModelsSignals(TestCase):
    def setUp(self):
        # Create tutors groups
        Group.objects.get_or_create(name='tutors')

    def test_assign_group_person_without_user(self):
        person = PersonFactory(user=None)
        signals._assign_group(person, "tutors")
        self.assertFalse(User.objects.filter(groups__name='tutors').count())

    def test_assign_group_person_with_user(self):
        person = PersonFactory()
        signals._assign_group(person, "tutors")
        self.assertEqual(1, User.objects.filter(groups__name='tutors').count())

    def test_assign_group_multiple_time_same_user(self):
        person = PersonFactory()
        signals._assign_group(person, "tutors")
        signals._assign_group(person, "tutors")
        signals._assign_group(person, "tutors")
        self.assertEqual(1, User.objects.filter(groups__name='tutors').count())

    def test_create_tutor_check_if_assign_to_group(self):
        person = PersonFactory()
        tutor = Tutor(person=person)
        tutor.save()
        self.assertEqual(1, User.objects.filter(groups__name='tutors').count())
        self.assertEqual(person.user, User.objects.filter(groups__name='tutors')[0])

    def test_create_tutor_and_update_user(self):
        person = PersonFactory()
        tutor = Tutor(person=person)
        tutor.save()

        # Update user
        user = person.user
        user.email = "toto@gmail.com"
        user.save()
        signals._assign_group(person, "tutors")

        self.assertEqual(1, User.objects.filter(groups__name='tutors').count())
        self.assertEqual(person.user, User.objects.filter(groups__name='tutors')[0])