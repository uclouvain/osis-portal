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
import datetime
from types import SimpleNamespace
from unittest import mock

from django.contrib.auth.models import Permission
from django.test import TestCase, RequestFactory
from django.urls import reverse
from osis_learning_unit_enrollment_sdk.model.enrollment import Enrollment

from attribution.tests.factories.enrollment import EnrollmentDictFactory
from attribution.views import students_list
from attribution.views.students_list import StudentsListView
from base.tests.factories.person import PersonFactory
from base.tests.factories.tutor import TutorFactory
from base.tests.models import test_academic_year
from performance.tests.models import test_student_performance


# TODO: Rewrite test because not lisible!!!
class StudentsListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.person = PersonFactory()
        perm = Permission.objects.get(codename="can_access_attribution")
        cls.person.user.user_permissions.add(perm)
        cls.current_year = datetime.date.today().year
        cls.a_tutor = TutorFactory(person=cls.person)
        cls.acronym = 'LELEC1530'
        cls.year = cls.current_year
        cls.url = reverse('student_enrollments_by_learning_unit', args=[
            cls.acronym, cls.year
        ])
        cls.students_list_view = StudentsListView(kwargs={
            'learning_unit_acronym': cls.acronym,
            'learning_unit_year': cls.year
        })

    def setUp(self):
        self.enrollments = SimpleNamespace(**{
            'results': [Enrollment(**EnrollmentDictFactory()) for _ in range(2)],
            'count': 1,
            'enrolled_students_count': 1,
            'attribute_map': dict.fromkeys({'results', 'count', 'enrolled_students_count'})
        })
        self.client.force_login(self.person.user)

    def _get_enrollment_for_acronym(self, acronym, mock_enrollments):
        student_performance = test_student_performance.create_student_performance()
        an_academic_yr = test_academic_year.create_academic_year_with_year(student_performance.academic_year)
        year = an_academic_yr.year
        enrollment = Enrollment(**EnrollmentDictFactory(
            student_registration_id=student_performance.registration_id,
            learning_unit_year=year,
            learning_unit_acronym=acronym,
            program=student_performance.acronym
        ))
        self.enrollments.results.append(enrollment)
        mock_enrollments.return_value = self.enrollments
        return enrollment

    @mock.patch("attribution.services.enrollments.LearningUnitEnrollmentService.get_enrollments")
    def test_find_january_note(self, mock_enrollments, acronym='LINGI2145', class_code=None):
        enrollment = self._get_enrollment_for_acronym(acronym, mock_enrollments)
        students_list_view = StudentsListView(kwargs={
            'learning_unit_year': str(enrollment.learning_unit_year),
            'learning_unit_acronym': acronym,
            'class_code': class_code,
        })
        request = RequestFactory().get('/')
        request.user = PersonFactory().user
        students_list_view.request = request

        self.assertEqual(
            students_list_view.get_sessions_results(enrollment), {
                    students_list.JANUARY: {
                         students_list.JSON_LEARNING_UNIT_NOTE: '13.0',
                         students_list.JSON_LEARNING_UNIT_STATUS: 'I'
                     },
                    students_list.JUNE: {
                         students_list.JSON_LEARNING_UNIT_NOTE: '13.0',
                         students_list.JSON_LEARNING_UNIT_STATUS: 'R'
                    },
                    students_list.SEPTEMBER: {
                         students_list.JSON_LEARNING_UNIT_NOTE: '-',
                         students_list.JSON_LEARNING_UNIT_STATUS: '-'
                    }
            }
        )

    def test_find_january_note_partim(self):
        acronym = 'LINGI2145B'
        self.test_find_january_note(acronym=acronym)

    def test_find_january_note_class(self):
        acronym = 'LINGI2145-A'
        self.test_find_january_note(acronym=acronym, class_code='A')

    def test_get_student_performance_data_dict(self):
        student_performance = test_student_performance.create_student_performance()
        self.assertEqual(self.students_list_view.get_student_data_dict(student_performance), student_performance.data)

    def test_get_no_student_performance_data_dict(self):
        self.assertIsNone(self.students_list_view.get_student_data_dict(None))

    @mock.patch("attribution.services.enrollments.LearningUnitEnrollmentService.get_enrollments")
    @mock.patch(
        "attribution.views.students_list.StudentsListView.learning_unit_title",
        new_callable=mock.PropertyMock, return_value="TITLE"
    )
    @mock.patch(
        "attribution.views.students_list.StudentsListView.learning_unit_type",
        new_callable=mock.PropertyMock, return_value="COURSE"
    )
    @mock.patch("attribution.views.students_list.StudentsListView.has_peps_student", return_value=True)
    def test_get_learning_unit_enrollments_list(self, mock_peps, mock_title, mock_type, mock_enrollments):
        mock_enrollments.return_value = SimpleNamespace(**{
            'count': 2,
            'enrolled_students_count': 2,
            'results': [
                Enrollment(
                    **EnrollmentDictFactory(
                        learning_unit_acronym=self.acronym,
                        program=program,
                    )
                ) for program in ['PROG2', 'PROG1']
            ],
            'attribute_map': dict.fromkeys({'results', 'count', 'enrolled_students_count'}),
        })
        response = self.client.get(self.url, follow=True)
        self.assertEqual(len(response.context['students']), 2)
        self.assertEqual(response.context['learning_unit_title'], "TITLE")
        self.assertEqual(response.context['has_peps'], True)
