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
from django.contrib.auth.models import User, Group
from django.test import TestCase
from attribution.tests.views import test_teaching_load

now = datetime.datetime.now()

CURRENT_YEAR = now.year + 1
NEXT_YEAR = now.year + 2

class OnlineApplicationTest(TestCase):

    def setUp(self):
        self.a_user = self.create_user(username='legat', email='legat@localhost', password='top_secret')
        self.a_person = test_person.create_person_with_user(self.a_user)
        Group.objects.get_or_create(name='tutors')
        self.a_tutor = test_tutor.create_tutor_with_person(self.a_person)
        self.data = []
        self.data.append(test_teaching_load.create_learning_unit_year_annual_data(CURRENT_YEAR))
        self.data.append(test_teaching_load.create_learning_unit_year_annual_data(NEXT_YEAR))
