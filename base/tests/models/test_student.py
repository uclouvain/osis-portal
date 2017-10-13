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
from django.contrib.auth.models import Group
from django.test import TestCase, Client
from django.http.request import HttpRequest
from django.contrib.admin.sites import site as admin_site

from base.tests.models.test_person import create_person
from base.tests.factories.student import StudentFactory
from base.tests.factories.person import PersonFactory
from base import models as mdl_base
from base.models import student as mdl_student


class TestModelStudent(TestCase):
    def setUp(self):
        Group.objects.create(name='students')
        self.student = StudentFactory()

    def test_email(self):
        self.student.person.user.email = "temp@email.com"
        self.student.person.user.save()
        self.assertEqual(self.student.email(),
                         self.student.person.user.email)

        self.student.person.user = None
        self.student.person.save()
        self.assertEqual(self.student.email(),
                         self.student.person.email)

    def test_find_by_registration_id(self):
        student = mdl_student.find_by_registration_id(self.student.registration_id)
        self.assertEqual(student, self.student)

    def test_search(self):
        self.assertEqual(mdl_student.search(), None)

        self.assertListEqual(list(mdl_student.search(registration_id=self.student.registration_id[:5])),
                             [self.student])
        self.assertListEqual(list(mdl_student.search(person_name=self.student.person.last_name)),
                             [self.student])
        self.assertListEqual(list(mdl_student.search(person_username=self.student.person.user.username)),
                             [self.student])
        self.assertListEqual(list(mdl_student.search(person_first_name=self.student.person.first_name)),
                             [self.student])
        self.assertListEqual(list(mdl_student.search(registration_id=self.student.registration_id,
                                                     full_registration=True)),
                             [self.student])

    def test_is_student(self):
        a_person = PersonFactory()

        self.assertFalse(mdl_student.is_student(a_person.user))

        self.assertTrue(mdl_student.is_student(self.student.person.user))


class StudentAdminTest(TestCase):
    def test_add_to_group(self):
        group_name = 'students'
        student_group = Group.objects.create(name=group_name)

        a_student = StudentFactory()
        student_group.user_set.remove(a_student.person.user)
        a_student_admin = mdl_student.StudentAdmin(mdl_student.Student, admin_site)

        a_request = Client().request().wsgi_request
        a_queryset = mdl_student.Student.objects.all()

        a_student_admin.add_to_group(a_request, a_queryset)

        self.assertTrue(a_student.person.user.groups.filter(name=group_name).exists())

        messages = list(a_request._messages)
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].tags, 'success')
        self.assertEqual(messages[0].message, "{} users added to the group '{}'.".format(1, group_name))

        student_group.delete()

        a_request = Client().request().wsgi_request
        a_student_admin.add_to_group(a_request, a_queryset)

        messages = list(a_request._messages)
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].tags, 'error')
        self.assertEqual(messages[0].message, "Group {} doesn't exist.".format(group_name))


def create_student(registration_id="64641200"):
    a_student = mdl_base.student.Student(registration_id=registration_id, person=create_person())
    a_student.save()
    return a_student


def create_student_with_specific_registration_id(registration_id):
    a_student = mdl_base.student.Student(registration_id=registration_id, person=create_person())
    a_student.save()
    return a_student


def create_student_with_registration_person(a_registration_id, a_person):
    a_student = mdl_base.student.Student()
    a_student.registration_id = a_registration_id
    a_student.person = a_person
    a_student.save()
    return a_student