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
from unittest.mock import patch
from django.contrib.auth.models import User, Group
from django.test import TestCase, Client
import json
import random
from base.tests.models import test_student, test_person, test_academic_year


def load_json_file(path):
    json_data = open(path)
    data1 = json.load(json_data) # deserialises it
    return data1


def _create_group(name):
    group = Group(name=name)
    return group.save()


class ExamEnrollmentFormTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.academic_year = test_academic_year.create_academic_year()
        group = _create_group('students')
        # self.user.groups.add(group)
        self.user = User.objects.create_user(username='jsmith', email='jsmith@localhost', password='secret')
        self.person = test_person.create_person_with_user(self.user, first_name="James", last_name="Smith")
        self.student = test_student.create_student_with_registration_person("12345678", self.person)
        self.url = '1234/form/'
        self.correct_exam_enrol_form = load_json_file("exam_enrollment/tests/ressources/exam_enrollment_form_example.json")

    def test_json_form_content(self):
        form = self.correct_exam_enrol_form
        self.assertTrue(form.get('registration_id'))
        self.assertTrue(form.get('current_number_session'))
        exam_enrollments = form.get('exam_enrollments')
        self.assertTrue(exam_enrollments)
        random_exam_enrol_position = random.randrange(len(exam_enrollments))
        random_exam_enrol = exam_enrollments[random_exam_enrol_position]
        self.assertTrue('credits' in random_exam_enrol.keys())
        self.assertTrue('credited' in random_exam_enrol.keys())
        self.assertTrue('enrolled_by_default' in random_exam_enrol.keys())
        self.assertTrue('session_1' in random_exam_enrol.keys()
                        or 'session_2' in random_exam_enrol.keys()
                        or 'session_3' in random_exam_enrol.keys())
        self.assertTrue(random_exam_enrol.get('learning_unit_year'))

    @patch("osis_common.queue.queue_sender.send_message")
    def test_exam_enrollment_form(self, mock_send_message):
        mock_send_message.return_value = self.correct_exam_enrol_form
        # self.client.login(username='jsmith', password='secret')
        response = self.client.get(self.url)
        print(str(response))
        print("------------------")
        print(str(response.context))
        print("------------------")
        print(str(response.content))
        print("------------------")
        self.assertEqual(response.status_code, 200)
        self.assertTrue('exam_enrollments' in response.context)
        self.assertTrue('student' in response.context)
        self.assertTrue('current_number_session' in response.context)
        self.assertTrue('academic_year' in response.context)
        self.assertTrue('program' in response.context)

    def test_return_content(self):
        pass






