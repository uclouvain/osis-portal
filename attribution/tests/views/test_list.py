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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
import datetime
from types import SimpleNamespace

import mock
from django.contrib.auth.models import Group, Permission
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from osis_attribution_sdk.model.attribution import Attribution
from osis_assessments_sdk.model.current_session import CurrentSession
from attribution.tests.factories.enrollment import EnrollmentDictFactory
from attribution.views.list import LEARNING_UNIT_ACRONYM_ID
from base.tests.factories.academic_year import AcademicYearFactory, create_current_academic_year
from base.tests.factories.learning_container_year import LearningContainerYearFactory
from base.tests.factories.learning_unit_year import LearningUnitYearFactory
from base.tests.factories.person import PersonFactory
from base.tests.factories.tutor import TutorFactory

ACCESS_DENIED = 401
METHOD_NOT_ALLOWED = 405
OK = 200


def return_sample_xls(*args):
    sample_path = 'attribution/tests/resources/sample.xls'
    with open(sample_path) as f:
        return f


class StudentsListTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Group.objects.create(name="tutors")
        Group.objects.get_or_create(name='students')
        cls.tutor = TutorFactory()
        person = cls.tutor.person
        person.global_id = "001923265"
        person.user.user_permissions.add(Permission.objects.get(codename="can_access_attribution"))
        person.save()
        cls.learning_unit_year = LearningUnitYearFactory()
        cls.enrollments = SimpleNamespace(**{
            'results': [SimpleNamespace(**EnrollmentDictFactory()) for _ in range(2)],
            'count': 1,
            'enrolled_students_count': 1,
            'attribute_map': dict.fromkeys({'results', 'count', 'enrolled_students_count'})
        })
        cls.url = reverse('students_list')

    def setUp(self):
        self.client.force_login(self.tutor.person.user)

    def test_without_being_logged(self):
        self.client.logout()
        response = self.client.get(self.url)

        self.assertRedirects(response, '/login/?next={}'.format(self.url))

    def test_without_permission(self):
        a_person = PersonFactory()
        self.client.force_login(a_person.user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, ACCESS_DENIED)
        self.assertTemplateUsed(response, 'access_denied.html')

    @mock.patch("assessments.services.assessments.AssessmentsService.get_current_session")
    @mock.patch("attribution.views.list.AttributionService.get_attributions_list")
    def test_with_no_attributions(self, mock_get_attributions_list, mock_get_current_session):
        mock_get_attributions_list.return_value = []
        mock_get_current_session = CurrentSession(academic_year="2021-22", month_session_name='January')
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, OK)
        self.assertTemplateUsed(response, 'list/students_exam.html')

        self.assertEqual(response.context['person'], self.tutor.person)
        self.assertEqual(response.context['my_learning_units'], [])

    @mock.patch("attribution.views.list.AttributionService.get_attributions_list")
    @mock.patch("attribution.views.list.LearningUnitService.get_learning_units")
    @mock.patch("attribution.views.list.AssessmentsService.get_score_responsible_list")
    @mock.patch("attribution.views.list.AssessmentsService.get_current_session")
    def test_with_attributions(self,
                               mock_current_session,
                               mock_get_score_responsible_list,
                               mock_get_learning_units,
                               mock_get_attributions_list
                               ):
        an_academic_year = create_current_academic_year()

        a_learning_unit_year = LearningUnitYearFactory(academic_year=an_academic_year)
        mock_get_attributions_list.return_value = [
            Attribution(
                code=a_learning_unit_year.acronym,
                year=a_learning_unit_year.academic_year.year,
                effective_class_repartition=[],
            )
        ]
        mock_get_learning_units.return_value = [
            {'acronym': a_learning_unit_year.acronym},
        ]
        mock_get_score_responsible_list.return_value = [
        ]
        mock_current_session.return_value = CurrentSession(
            academic_year=str(an_academic_year),
            month_session_name='January',
            year=an_academic_year.year,
        )
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, OK)
        self.assertTemplateUsed(response, 'list/students_exam.html')

        self.assertEqual(response.context['person'], self.tutor.person)

    @mock.patch("attribution.views.list.AttributionService.get_attributions_list")
    @mock.patch("attribution.services.enrollments.LearningUnitEnrollmentService.get_enrollments")
    @mock.patch("attribution.views.students_list.StudentsListView.learning_unit_title", new_callable=mock.PropertyMock)
    def test_with_attribution_students(self, mock_lu, mock_students_list_endpoint, mock_get_attributions_list):
        mock_students_list_endpoint.return_value = self.enrollments
        mock_lu.return_value = "TITLE"
        today = datetime.datetime.today()
        an_academic_year = AcademicYearFactory(
            year=today.year, start_date=today - datetime.timedelta(days=5),
            end_date=today + datetime.timedelta(days=5)
        )
        a_learning_unit_year = LearningUnitYearFactory(academic_year=an_academic_year)
        mock_get_attributions_list.return_value = [
            {
                'code': a_learning_unit_year.acronym,
                'year': a_learning_unit_year.academic_year.year,
                'has_peps': False
            }
        ]
        url = reverse('student_enrollments_by_learning_unit', kwargs={
            'learning_unit_acronym': a_learning_unit_year.acronym,
            'learning_unit_year': a_learning_unit_year.academic_year.year
        })
        response = self.client.get(url)
        self.assertEqual(response.status_code, OK)
        self.assertTemplateUsed(response, 'students_list.html')

        self.assertEqual(response.context['global_id'], self.tutor.person.global_id)
        self.assertEqual(response.context['learning_unit_year'], str(a_learning_unit_year.academic_year.year))
        self.assertEqual(response.context['learning_unit_acronym'], str(a_learning_unit_year.acronym))
        self.assertEqual(response.context['learning_unit_title'], "TITLE")
        self.assertTrue(response.context['students'])
        self.assertEqual(len(response.context['students']), 2)


class ListBuildTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Group.objects.create(name="tutors")
        cls.tutor = TutorFactory()
        cls.tutor.person.user.user_permissions.add(Permission.objects.get(codename="can_access_attribution"))

        cls.url = reverse('students_list_create')

    def setUp(self):
        self.client.force_login(self.tutor.person.user)

    def test_without_being_logged(self):
        self.client.logout()
        response = self.client.post(self.url)

        self.assertRedirects(response, '/login/?next={}'.format(self.url))

    def test_without_permission(self):
        a_person = PersonFactory()
        self.client.force_login(a_person.user)
        response = self.client.post(self.url)

        self.assertEqual(response.status_code, ACCESS_DENIED)
        self.assertTemplateUsed(response, 'access_denied.html')

    def test_with_get(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, METHOD_NOT_ALLOWED)

    @mock.patch("attribution.views.list.AttributionService.get_attributions_list")
    @mock.patch("attribution.views.list.LearningUnitService.get_learning_units")
    @mock.patch("attribution.views.list.AssessmentsService.get_score_responsible_list")
    @mock.patch("attribution.views.list.AssessmentsService.get_current_session")
    def test_with_empty_post(self,
                             mock_current_session,
                             mock_get_score_responsible_list,
                             mock_get_learning_units,
                             mock_get_attributions_list):
        mock_get_attributions_list.return_value = []
        mock_get_learning_units.return_value = []
        mock_get_score_responsible_list.return_value = []
        mock_current_session.return_value = None
        response = self.client.post(self.url)

        self.assertEqual(response.status_code, OK)
        self.assertTemplateUsed(response, 'list/students_exam.html')

        self.assertEqual(response.context['person'], self.tutor.person)
        self.assertEqual(response.context['my_learning_units'], [])
        self.assertEqual(response.context['msg_error'], _('No data found'))

    @override_settings(ATTRIBUTION_CONFIG={
        'SERVER_TO_FETCH_URL': '/server',
        'ATTRIBUTION_PATH': '/path'
    })
    @mock.patch("attribution.views.list.AttributionService.get_attributions_list")
    @mock.patch("attribution.views.list.LearningUnitService.get_learning_units")
    @mock.patch("attribution.views.list.AssessmentsService.get_score_responsible_list")
    @mock.patch("attribution.views.list.AssessmentsService.get_current_session")
    @mock.patch('attribution.views.list._fetch_with_basic_auth', side_effect=Exception)
    def test_with_post_but_webservice_unavailable(self,
                                                  mock_fetch,
                                                  mock_current_session,
                                                  mock_get_score_responsible_list,
                                                  mock_get_learning_units,
                                                  mock_get_attributions_list
                                                  ):
        today = datetime.datetime.today()
        an_academic_year = AcademicYearFactory(year=today.year, start_date=today - datetime.timedelta(days=5),
                                               end_date=today + datetime.timedelta(days=5))
        learning_container_year = LearningContainerYearFactory(academic_year=an_academic_year)
        a_learning_unit_year = LearningUnitYearFactory(
            academic_year=an_academic_year,
            learning_container_year=learning_container_year
        )
        mock_get_attributions_list.return_value = [
            Attribution(
                code=a_learning_unit_year.acronym,
                year=a_learning_unit_year.academic_year.year,
                effective_class_repartition=[],
            )
        ]
        mock_get_learning_units.return_value = [
            {'acronym': a_learning_unit_year.acronym},
        ]
        mock_get_score_responsible_list.return_value = [
        ]
        mock_current_session.return_value = CurrentSession(
            academic_year=str(an_academic_year),
            month_session_name='January',
            year=an_academic_year.year,
        )
        key = '{}{}'.format(LEARNING_UNIT_ACRONYM_ID, a_learning_unit_year.acronym)
        response = self.client.post(self.url, data={key: ""})

        self.assertTrue(mock_fetch.called)

        self.assertEqual(response.status_code, OK)
        self.assertTemplateUsed(response, 'list/students_exam.html')

        self.assertEqual(response.context['person'], self.tutor.person)
        self.assertEqual(response.context['msg_error'], _('No data found'))

    @mock.patch("attribution.views.list.AttributionService.get_attributions_list")
    @mock.patch("attribution.views.list.LearningUnitService.get_learning_units")
    @mock.patch("attribution.views.list.AssessmentsService.get_score_responsible_list")
    @mock.patch("attribution.views.list.AssessmentsService.get_current_session")
    def test_when_trying_to_access_other_tutor_students_list(self,
                                                             mock_current_session,
                                                             mock_get_score_responsible_list,
                                                             mock_get_learning_units,
                                                             mock_get_attributions_list):
        an_other_tutor = TutorFactory()
        an_other_tutor.person.user.user_permissions.add(Permission.objects.get(codename="can_access_attribution"))
        self.client.force_login(an_other_tutor.person.user)
        today = datetime.datetime.today()
        an_academic_year = AcademicYearFactory(year=today.year, start_date=today - datetime.timedelta(days=5),
                                               end_date=today + datetime.timedelta(days=5))
        a_learning_unit_year = LearningUnitYearFactory(academic_year=an_academic_year)
        mock_get_attributions_list.return_value = []
        mock_get_score_responsible_list.return_value = [
        ]
        mock_get_learning_units.return_value = [
            {'acronym': a_learning_unit_year.acronym},
        ]
        mock_current_session.return_value = CurrentSession(
            academic_year=str(an_academic_year),
            month_session_name='January',
            year=an_academic_year.year,
        )
        key = '{}{}'.format(LEARNING_UNIT_ACRONYM_ID, a_learning_unit_year.acronym)
        response = self.client.post(self.url, data={key: ""})

        self.assertEqual(response.status_code, OK)
        self.assertTemplateUsed(response, 'list/students_exam.html')

        self.assertEqual(response.context['person'], an_other_tutor.person)
        expected_learning_unit_data = {
            'acronym': a_learning_unit_year.acronym,
            'learning_unit': {'acronym': a_learning_unit_year.acronym,
                              'effective_class_detail': [],
                              'score_responsible': ''
                              },
        }
        self.assertEqual(len(response.context['my_learning_units']), 1)
        self.assertEqual(response.context['my_learning_units'][0], expected_learning_unit_data)
        self.assertEqual(response.context['msg_error'], _('No data found'))

    @override_settings(ATTRIBUTION_CONFIG={
        'SERVER_TO_FETCH_URL': '/server',
        'ATTRIBUTION_PATH': '/path'
    })
    @mock.patch("attribution.views.list.AttributionService.get_attributions_list")
    @mock.patch("attribution.views.list.LearningUnitService.get_learning_units")
    @mock.patch("attribution.views.list.AssessmentsService.get_score_responsible_list")
    @mock.patch("attribution.views.list.AssessmentsService.get_current_session")
    @mock.patch('attribution.views.list._fetch_with_basic_auth', side_effect=return_sample_xls)
    def test_with_post_and_webservice_is_available(self,
                                                   mock_fetch,
                                                   mock_current_session,
                                                   mock_get_score_responsible_list,
                                                   mock_get_learning_units,
                                                   mock_get_attributions_list
                                                   ):
        today = datetime.datetime.today()
        an_academic_year = AcademicYearFactory(year=today.year, start_date=today - datetime.timedelta(days=5),
                                               end_date=today + datetime.timedelta(days=5))
        a_learning_container_year = LearningContainerYearFactory(academic_year=an_academic_year)
        a_learning_unit_year = LearningUnitYearFactory(
            academic_year=an_academic_year,
            learning_container_year=a_learning_container_year
        )
        mock_get_attributions_list.return_value = [
            Attribution(
                code=a_learning_unit_year.acronym,
                year=a_learning_unit_year.academic_year.year,
                effective_class_repartition=[],
            )
        ]
        mock_get_learning_units.return_value = [
            {'acronym': a_learning_unit_year.acronym},
        ]
        mock_get_score_responsible_list.return_value = [
        ]
        mock_current_session.return_value = CurrentSession(
            academic_year=str(an_academic_year),
            month_session_name='January',
            year=an_academic_year.year,
        )

        key = '{}{}'.format(LEARNING_UNIT_ACRONYM_ID, a_learning_unit_year.acronym)
        response = self.client.post(self.url, data={key: ""})

        filename = "Liste_Insc_Exam.xls"
        self.assertEqual(response.status_code, OK)
        self.assertTrue(mock_fetch.called)
        self.assertEqual(response['Content-Type'],
                         'application/vnd.ms-excel')
        self.assertEqual(response['Content-Disposition'], 'attachment; filename="{}"'.format(filename))
        self.assertEqual(response.content.decode(), str(return_sample_xls()))


class AdminStudentsListTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Group.objects.create(name="tutors")
        cls.person = PersonFactory(global_id="76543210")
        cls.tutor = TutorFactory(person=cls.person)
        cls.tutor.person.user.user_permissions.add(Permission.objects.get(codename="can_access_attribution"))

        cls.url = reverse('lists_of_students_exams_enrollments')

    def setUp(self):
        self.client.force_login(self.tutor.person.user)

    def test_without_being_logged(self):
        self.client.logout()
        response = self.client.get(self.url)

        self.assertRedirects(response, '/login/?next={}'.format(self.url))

    def test_without_permission(self):
        a_person = PersonFactory()
        self.client.force_login(a_person.user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, ACCESS_DENIED)
        self.assertTemplateUsed(response, 'access_denied.html')

    @mock.patch("attribution.views.list.AssessmentsService.get_score_responsible_list")
    def test_with_no_attributions(self, mock_get_score_responsible_list):
        response = self.client.get(self.url)
        mock_get_score_responsible_list.return_value = [
        ]
        self.assertEqual(response.status_code, OK)
        self.assertTemplateUsed(response, 'admin/students_list.html')

    @mock.patch("attribution.views.list.AttributionService.get_attributions_list")
    def test_with_attributions(self, mock_get_attributions_list):
        today = datetime.datetime.today()
        an_academic_year = AcademicYearFactory(year=today.year, start_date=today - datetime.timedelta(days=5),
                                               end_date=today + datetime.timedelta(days=5))
        a_learning_unit_year = LearningUnitYearFactory(academic_year=an_academic_year)
        mock_get_attributions_list.return_value = [
            Attribution(
                code=a_learning_unit_year.acronym,
                year=a_learning_unit_year.academic_year.year,
                effective_class_repartition=[],
            )
        ]

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, OK)
        self.assertTemplateUsed(response, 'admin/students_list.html')


class AdminListBuildTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Group.objects.create(name="tutors")
        cls.person = PersonFactory(global_id="01234567")
        cls.tutor = TutorFactory(person=cls.person)
        cls.tutor.person.user.user_permissions.add(Permission.objects.get(codename="can_access_attribution"))

        cls.url = reverse('lists_of_students_exams_enrollments_create', args=['01234567'])

    def setUp(self):
        self.client.force_login(self.tutor.person.user)

    def test_without_being_logged(self):
        self.client.logout()
        response = self.client.post(self.url)

        self.assertRedirects(response, '/login/?next={}'.format(self.url))

    def test_without_permission(self):
        a_person = PersonFactory()
        self.client.force_login(a_person.user)
        response = self.client.post(self.url)

        self.assertEqual(response.status_code, ACCESS_DENIED)
        self.assertTemplateUsed(response, 'access_denied.html')

    def test_with_get(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, METHOD_NOT_ALLOWED)

    @mock.patch("attribution.views.list.AttributionService.get_attributions_list")
    @mock.patch("attribution.views.list.LearningUnitService.get_learning_units")
    @mock.patch("attribution.views.list.AssessmentsService.get_score_responsible_list")
    @mock.patch("attribution.views.list.AssessmentsService.get_current_session")
    def test_with_empty_post(self,
                             mock_current_session,
                             mock_get_score_responsible_list,
                             mock_get_learning_units,
                             mock_get_attributions_list):
        mock_get_attributions_list.return_value = []
        mock_get_learning_units.return_value = []
        mock_get_score_responsible_list.return_value = []
        mock_current_session.return_value = None
        response = self.client.post(self.url, )

        self.assertEqual(response.status_code, OK)
        self.assertTemplateUsed(response, 'admin/students_exam_list.html')

        self.assertEqual(response.context['person'], self.tutor.person)
        self.assertEqual(response.context['learning_units'], [])
        self.assertEqual(response.context['msg_error'], _('No data found'))

    @override_settings(ATTRIBUTION_CONFIG={
        'SERVER_TO_FETCH_URL': '/server',
        'ATTRIBUTION_PATH': '/path'
    })
    @mock.patch("attribution.views.list.AttributionService.get_attributions_list")
    @mock.patch("attribution.views.list.LearningUnitService.get_learning_units")
    @mock.patch("attribution.views.list.AssessmentsService.get_score_responsible_list")
    @mock.patch("attribution.views.list.AssessmentsService.get_current_session")
    @mock.patch('attribution.views.list._fetch_with_basic_auth', side_effect=Exception)
    def test_with_post_but_webservice_unavailable(self,
                                                  mock_fetch,
                                                  mock_current_session,
                                                  mock_get_score_responsible_list,
                                                  mock_get_learning_units,
                                                  mock_get_attributions_list):
        today = datetime.datetime.today()
        an_academic_year = AcademicYearFactory(year=today.year, start_date=today - datetime.timedelta(days=5),
                                               end_date=today + datetime.timedelta(days=5))
        a_learning_unit_year = LearningUnitYearFactory(academic_year=an_academic_year,
                                                       learning_container_year__academic_year=an_academic_year)
        mock_get_attributions_list.return_value = [
            Attribution(
                code=a_learning_unit_year.acronym,
                year=a_learning_unit_year.academic_year.year,
                effective_class_repartition=[],
            )
        ]
        mock_get_learning_units.return_value = [
            {'acronym': a_learning_unit_year.acronym},
        ]
        mock_get_score_responsible_list.return_value = [
        ]
        mock_current_session.return_value = CurrentSession(
            academic_year=str(an_academic_year),
            month_session_name='January',
            year=an_academic_year.year,
        )
        key = '{}{}'.format(LEARNING_UNIT_ACRONYM_ID, a_learning_unit_year.acronym)
        response = self.client.post(self.url, data={key: ""})

        self.assertTrue(mock_fetch.called)

        self.assertEqual(response.status_code, OK)
        self.assertTemplateUsed(response, 'admin/students_exam_list.html')

        self.assertEqual(response.context['person'], self.tutor.person)

        expected_learning_unit_data = {
            'acronym': a_learning_unit_year.acronym,
            'learning_unit': {'acronym': a_learning_unit_year.acronym,
                              'effective_class_detail': [],
                              'score_responsible': ''
                              },
        }

        self.assertEqual(len(response.context['learning_units']), 1)
        self.assertEqual(response.context['learning_units'][0], expected_learning_unit_data)
        self.assertEqual(response.context['msg_error'], _('No data found'))

    @override_settings(ATTRIBUTION_CONFIG={
        'SERVER_TO_FETCH_URL': '/server',
        'ATTRIBUTION_PATH': '/path'
    })
    @mock.patch("attribution.views.list.AttributionService.get_attributions_list")
    @mock.patch("attribution.views.list.LearningUnitService.get_learning_units")
    @mock.patch("attribution.views.list.AssessmentsService.get_score_responsible_list")
    @mock.patch("attribution.views.list.AssessmentsService.get_current_session")
    @mock.patch('attribution.views.list._fetch_with_basic_auth', side_effect=return_sample_xls)
    def test_with_post_and_webservice_is_available(self,
                                                   mock_fetch,
                                                   mock_current_session,
                                                   mock_get_score_responsible_list,
                                                   mock_get_learning_units,
                                                   mock_get_attributions_list):
        today = datetime.datetime.today()
        an_academic_year = AcademicYearFactory(year=today.year, start_date=today - datetime.timedelta(days=5),
                                               end_date=today + datetime.timedelta(days=5))
        a_learning_unit_year = LearningUnitYearFactory(academic_year=an_academic_year,
                                                       learning_container_year__academic_year=an_academic_year)
        mock_get_attributions_list.return_value = [
            Attribution(
                code=a_learning_unit_year.acronym,
                year=a_learning_unit_year.academic_year.year,
                effective_class_repartition=[]
            )
        ]
        mock_get_learning_units.return_value = [
            {'acronym': a_learning_unit_year.acronym},
        ]
        mock_get_score_responsible_list.return_value = [
        ]
        mock_current_session.return_value = CurrentSession(
            academic_year=str(an_academic_year),
            month_session_name='January',
            year=an_academic_year.year,
        )
        key = '{}{}'.format(LEARNING_UNIT_ACRONYM_ID, a_learning_unit_year.acronym)
        response = self.client.post(self.url, data={key: ""})

        filename = "Liste_Insc_Exam.xls"
        self.assertEqual(response.status_code, OK)
        self.assertTrue(mock_fetch.called)
        self.assertEqual(response['Content-Type'],
                         'application/vnd.ms-excel')
        self.assertEqual(response['Content-Disposition'], 'attachment; filename="{}"'.format(filename))
        self.assertEqual(response.content.decode(), str(return_sample_xls()))
