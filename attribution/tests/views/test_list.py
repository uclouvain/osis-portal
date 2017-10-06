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

from django.contrib.auth.models import Group, Permission
from django.core.urlresolvers import reverse
from django.test import TestCase, Client

from base.tests.factories.tutor import TutorFactory
from base.tests.factories.person import PersonFactory
from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.learning_unit_year import LearningUnitYearFactory
from attribution.tests.factories.attribution import AttributionFactory


ACCESS_DENIED = 401
OK = 200


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






