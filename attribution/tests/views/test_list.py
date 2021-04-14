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

import mock
from django.contrib.auth.models import Group, Permission
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from osis_attribution_sdk.model.attribution import Attribution

from attribution.views.list import LEARNING_UNIT_ACRONYM_ID
from base.tests.factories.academic_year import AcademicYearFactory, create_current_academic_year
from base.tests.factories.learning_container_year import LearningContainerYearFactory
from base.tests.factories.learning_unit_enrollment import LearningUnitEnrollmentFactory
from base.tests.factories.learning_unit_year import LearningUnitYearFactory
from base.tests.factories.offer_enrollment import OfferEnrollmentFactory
from base.tests.factories.offer_year import OfferYearFactory
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

    def test_with_no_attributions(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, OK)
        self.assertTemplateUsed(response, 'list/students_exam.html')

        self.assertEqual(response.context['person'], self.tutor.person)
        self.assertEqual(response.context['my_learning_units'], [])

    @mock.patch("attribution.views.list.RemoteAttributionService.get_attributions_list")
    def test_with_attributions(self, mock_get_attributions_list):
        an_academic_year = create_current_academic_year()

        a_learning_unit_year = LearningUnitYearFactory(academic_year=an_academic_year)
        mock_get_attributions_list.return_value = [
            Attribution(
                code=a_learning_unit_year.acronym,
                year=a_learning_unit_year.academic_year.year,
            )
        ]
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, OK)
        self.assertTemplateUsed(response, 'list/students_exam.html')

        self.assertEqual(response.context['person'], self.tutor.person)
        self.assertListEqual(response.context['my_learning_units'], [a_learning_unit_year])

    @mock.patch("attribution.views.list.RemoteAttributionService.get_attributions_list")
    def test_with_attribution_students(self, mock_get_attributions_list):
        today = datetime.datetime.today()
        an_academic_year = AcademicYearFactory(year=today.year, start_date=today - datetime.timedelta(days=5),
                                               end_date=today + datetime.timedelta(days=5))
        a_learning_unit_year = LearningUnitYearFactory(academic_year=an_academic_year)
        mock_get_attributions_list.return_value = [
            Attribution(
                code=a_learning_unit_year.acronym,
                year=a_learning_unit_year.academic_year.year,
            )
        ]
        offer_year = OfferYearFactory(academic_year=an_academic_year)

        # Create two enrollment to exam [Enrolled]
        off_enrollment = OfferEnrollmentFactory(offer_year=offer_year)
        LearningUnitEnrollmentFactory(learning_unit_year=a_learning_unit_year, offer_enrollment=off_enrollment)
        off_enrollment = OfferEnrollmentFactory(offer_year=offer_year)
        LearningUnitEnrollmentFactory(learning_unit_year=a_learning_unit_year, offer_enrollment=off_enrollment)
        # Create an enrollment to exam [NOT enrolled]
        off_enrollment = OfferEnrollmentFactory(offer_year=offer_year)
        LearningUnitEnrollmentFactory(learning_unit_year=a_learning_unit_year, offer_enrollment=off_enrollment,
                                      enrollment_state="")

        url = reverse('attribution_students', kwargs={
            'learning_unit_year_id': a_learning_unit_year.id,
            'a_tutor': self.tutor.id
        })
        response = self.client.get(url)
        self.assertEqual(response.status_code, OK)
        self.assertTemplateUsed(response, 'students_list.html')

        self.assertEqual(response.context['global_id'], self.tutor.person.global_id)
        self.assertEqual(response.context['learning_unit_year'], a_learning_unit_year)
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

    def test_with_empty_post(self):
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
    @mock.patch("attribution.views.list.RemoteAttributionService.get_attributions_list")
    @mock.patch('attribution.views.list._fetch_with_basic_auth', side_effect=Exception)
    def test_with_post_but_webservice_unavailable(self, mock_fetch, mock_get_attributions_list):
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
            )
        ]
        key = '{}{}'.format(LEARNING_UNIT_ACRONYM_ID, a_learning_unit_year.acronym)
        response = self.client.post(self.url, data={key: ""})

        self.assertTrue(mock_fetch.called)

        self.assertEqual(response.status_code, OK)
        self.assertTemplateUsed(response, 'list/students_exam.html')

        self.assertEqual(response.context['person'], self.tutor.person)
        self.assertEqual(response.context['my_learning_units'], [a_learning_unit_year])
        self.assertEqual(response.context['msg_error'], _('No data found'))

    @mock.patch("attribution.views.list.RemoteAttributionService.get_attributions_list")
    def test_when_trying_to_access_other_tutor_students_list(self, mock_get_attributions_list):
        an_other_tutor = TutorFactory()
        an_other_tutor.person.user.user_permissions.add(Permission.objects.get(codename="can_access_attribution"))
        self.client.force_login(an_other_tutor.person.user)
        today = datetime.datetime.today()
        an_academic_year = AcademicYearFactory(year=today.year, start_date=today - datetime.timedelta(days=5),
                                               end_date=today + datetime.timedelta(days=5))
        a_learning_unit_year = LearningUnitYearFactory(academic_year=an_academic_year)
        mock_get_attributions_list.return_value = []

        key = '{}{}'.format(LEARNING_UNIT_ACRONYM_ID, a_learning_unit_year.acronym)
        response = self.client.post(self.url, data={key: ""})

        self.assertEqual(response.status_code, OK)
        self.assertTemplateUsed(response, 'list/students_exam.html')

        self.assertEqual(response.context['person'], an_other_tutor.person)
        self.assertEqual(response.context['my_learning_units'], [])
        self.assertEqual(response.context['msg_error'], _('No data found'))

    @override_settings(ATTRIBUTION_CONFIG={
        'SERVER_TO_FETCH_URL': '/server',
        'ATTRIBUTION_PATH': '/path'
    })
    @mock.patch("attribution.views.list.RemoteAttributionService.get_attributions_list")
    @mock.patch('attribution.views.list._fetch_with_basic_auth', side_effect=return_sample_xls)
    def test_with_post_and_webservice_is_available(self, mock_fetch, mock_get_attributions_list):
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
            )
        ]
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

    def test_with_no_attributions(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, OK)
        self.assertTemplateUsed(response, 'admin/students_list.html')

    @mock.patch("attribution.views.list.RemoteAttributionService.get_attributions_list")
    def test_with_attributions(self, mock_get_attributions_list):
        today = datetime.datetime.today()
        an_academic_year = AcademicYearFactory(year=today.year, start_date=today - datetime.timedelta(days=5),
                                               end_date=today + datetime.timedelta(days=5))
        a_learning_unit_year = LearningUnitYearFactory(academic_year=an_academic_year)
        mock_get_attributions_list.return_value = [
            Attribution(
                code=a_learning_unit_year.acronym,
                year=a_learning_unit_year.academic_year.year,
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

    def test_with_empty_post(self):
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
    @mock.patch("attribution.views.list.RemoteAttributionService.get_attributions_list")
    @mock.patch('attribution.views.list._fetch_with_basic_auth', side_effect=Exception)
    def test_with_post_but_webservice_unavailable(self, mock_fetch, mock_get_attributions_list):
        today = datetime.datetime.today()
        an_academic_year = AcademicYearFactory(year=today.year, start_date=today - datetime.timedelta(days=5),
                                               end_date=today + datetime.timedelta(days=5))
        a_learning_unit_year = LearningUnitYearFactory(academic_year=an_academic_year,
                                                       learning_container_year__academic_year=an_academic_year)
        mock_get_attributions_list.return_value = [
            Attribution(
                code=a_learning_unit_year.acronym,
                year=a_learning_unit_year.academic_year.year,
            )
        ]

        key = '{}{}'.format(LEARNING_UNIT_ACRONYM_ID, a_learning_unit_year.acronym)
        response = self.client.post(self.url, data={key: ""})

        self.assertTrue(mock_fetch.called)

        self.assertEqual(response.status_code, OK)
        self.assertTemplateUsed(response, 'admin/students_exam_list.html')

        self.assertEqual(response.context['person'], self.tutor.person)
        self.assertEqual(response.context['learning_units'], [a_learning_unit_year])
        self.assertEqual(response.context['msg_error'], _('No data found'))

    @override_settings(ATTRIBUTION_CONFIG={
        'SERVER_TO_FETCH_URL': '/server',
        'ATTRIBUTION_PATH': '/path'
    })
    @mock.patch("attribution.views.list.RemoteAttributionService.get_attributions_list")
    @mock.patch('attribution.views.list._fetch_with_basic_auth', side_effect=return_sample_xls)
    def test_with_post_and_webservice_is_available(self, mock_fetch, mock_get_attributions_list):
        today = datetime.datetime.today()
        an_academic_year = AcademicYearFactory(year=today.year, start_date=today - datetime.timedelta(days=5),
                                               end_date=today + datetime.timedelta(days=5))
        a_learning_unit_year = LearningUnitYearFactory(academic_year=an_academic_year,
                                                       learning_container_year__academic_year=an_academic_year)
        mock_get_attributions_list.return_value = [
            Attribution(
                code=a_learning_unit_year.acronym,
                year=a_learning_unit_year.academic_year.year,
            )
        ]
        key = '{}{}'.format(LEARNING_UNIT_ACRONYM_ID, a_learning_unit_year.acronym)
        response = self.client.post(self.url, data={key: ""})

        filename = "Liste_Insc_Exam.xls"
        self.assertEqual(response.status_code, OK)
        self.assertTrue(mock_fetch.called)
        self.assertEqual(response['Content-Type'],
                         'application/vnd.ms-excel')
        self.assertEqual(response['Content-Disposition'], 'attachment; filename="{}"'.format(filename))
        self.assertEqual(response.content.decode(), str(return_sample_xls()))
