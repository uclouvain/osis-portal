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
import datetime
<<<<<<< HEAD

from django.contrib.auth.models import Group, Permission
from django.core.urlresolvers import reverse
from django.test import TestCase, Client

=======
import mock

from django.contrib.auth.models import Group, Permission
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.test import TestCase, Client, override_settings

from attribution.views.list import LEARNING_UNIT_ACRONYM_ID
>>>>>>> 0877abe1956ded75f75efcd4c467e66e6e781e68
from base.tests.factories.tutor import TutorFactory
from base.tests.factories.person import PersonFactory
from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.learning_unit_year import LearningUnitYearFactory
from attribution.tests.factories.attribution import AttributionFactory


ACCESS_DENIED = 401
METHOD_NOT_ALLOWED = 405
OK = 200


def return_sample_xls(*args):
    sample_path = 'attribution/tests/resources/sample.xls'
    with open(sample_path) as f:
        return f


class StudentsListTest(TestCase):
    def setUp(self):
        Group.objects.create(name="tutors")
        self.tutor = TutorFactory()
        self.tutor.person.user.user_permissions.add(Permission.objects.get(codename="can_access_attribution"))

        self.url = reverse('students_list')
        self.client = Client()
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

    def test_with_attributions(self):
        today = datetime.datetime.today()
        an_academic_year = AcademicYearFactory(year=today.year, start_date=today-datetime.timedelta(days=5),
                                               end_date=today+datetime.timedelta(days=5))
        a_learning_unit_year = LearningUnitYearFactory(academic_year=an_academic_year)
        AttributionFactory(learning_unit_year=a_learning_unit_year, tutor=self.tutor)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, OK)
        self.assertTemplateUsed(response, 'list/students_exam.html')

        self.assertEqual(response.context['person'], self.tutor.person)
        self.assertListEqual(response.context['my_learning_units'], [a_learning_unit_year])


class ListBuildTest(TestCase):
    def setUp(self):
        Group.objects.create(name="tutors")
        self.tutor = TutorFactory()
        self.tutor.person.user.user_permissions.add(Permission.objects.get(codename="can_access_attribution"))

        self.url = reverse('students_list_create')
        self.client = Client()
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
        self.assertEqual(response.context['msg_error'], _('no_data'))

    @override_settings(ATTRIBUTION_CONFIG={'SERVER_TO_FETCH_URL': '/server',
                                           'ATTRIBUTION_PATH': '/path'})
    @mock.patch('attribution.views.list._fetch_with_basic_auth', side_effect=Exception)
    def test_with_post_but_webservice_unavailable(self, mock_fetch):
        today = datetime.datetime.today()
        an_academic_year = AcademicYearFactory(year=today.year, start_date=today - datetime.timedelta(days=5),
                                               end_date=today + datetime.timedelta(days=5))
        a_learning_unit_year = LearningUnitYearFactory(academic_year=an_academic_year)
        AttributionFactory(learning_unit_year=a_learning_unit_year, tutor=self.tutor)

        key = '{}{}'.format(LEARNING_UNIT_ACRONYM_ID, a_learning_unit_year.acronym)
        response = self.client.post(self.url, data={key: ""})

        self.assertTrue(mock_fetch.called)

        self.assertEqual(response.status_code, OK)
        self.assertTemplateUsed(response, 'list/students_exam.html')

        self.assertEqual(response.context['person'], self.tutor.person)
        self.assertEqual(response.context['my_learning_units'], [a_learning_unit_year])
        self.assertEqual(response.context['msg_error'], _('no_data'))

    def test_when_trying_to_access_other_tutor_students_list(self):
        an_other_tutor = TutorFactory()
        an_other_tutor.person.user.user_permissions.add(Permission.objects.get(codename="can_access_attribution"))
        self.client.force_login(an_other_tutor.person.user)
        today = datetime.datetime.today()
        an_academic_year = AcademicYearFactory(year=today.year, start_date=today - datetime.timedelta(days=5),
                                               end_date=today + datetime.timedelta(days=5))
        a_learning_unit_year = LearningUnitYearFactory(academic_year=an_academic_year)
        AttributionFactory(learning_unit_year=a_learning_unit_year, tutor=self.tutor)

        key = '{}{}'.format(LEARNING_UNIT_ACRONYM_ID, a_learning_unit_year.acronym)
        response = self.client.post(self.url, data={key: ""})

        self.assertEqual(response.status_code, OK)
        self.assertTemplateUsed(response, 'list/students_exam.html')

        self.assertEqual(response.context['person'], an_other_tutor.person)
        self.assertEqual(response.context['my_learning_units'], [])
        self.assertEqual(response.context['msg_error'], _('no_data'))

    @override_settings(ATTRIBUTION_CONFIG={'SERVER_TO_FETCH_URL': '/server',
                                           'ATTRIBUTION_PATH': '/path'})
    @mock.patch('attribution.views.list._fetch_with_basic_auth', side_effect=return_sample_xls)
    def test_with_post_and_webservice_is_available(self, mock_fetch):
        today = datetime.datetime.today()
        an_academic_year = AcademicYearFactory(year=today.year, start_date=today - datetime.timedelta(days=5),
                                               end_date=today + datetime.timedelta(days=5))
        a_learning_unit_year = LearningUnitYearFactory(academic_year=an_academic_year)
        AttributionFactory(learning_unit_year=a_learning_unit_year, tutor=self.tutor)

        key = '{}{}'.format(LEARNING_UNIT_ACRONYM_ID, a_learning_unit_year.acronym)
        response = self.client.post(self.url, data={key: ""})

        filename = "Liste_Insc_Exam.xls"
        self.assertEqual(response.status_code, OK)
        self.assertTrue(mock_fetch.called)
        self.assertEqual(response['Content-Type'], 'application/vnd.ms-excel')
        self.assertEqual(response['Content-Disposition'], 'attachment; filename="{}"'.format(filename))
        self.assertEqual(response.content.decode(), str(return_sample_xls()))






