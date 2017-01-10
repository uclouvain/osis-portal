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

from attribution.utils import generating_message
from base.models.enums import component_type
from attribution.models.enums import function
from base.tests.models import test_person, test_tutor, test_academic_year, test_learning_unit_year, \
    test_learning_unit_component
from attribution.tests.models import test_attribution_charge, test_attribution, test_application_charge, \
    test_tutor_application

now = datetime.datetime.now()
WEIGHT = 5
ACRONYM = 'LFSAB1003'
TITLE = 'METHODES NUMERIQUES'
CURRENT_YEAR = now.year


LEARNING_UNIT_LECTURING_DURATION = 15.00
LEARNING_UNIT_PRACTICAL_EXERCISES_DURATION = 30.00
CHARGE_NULL = 0


class TestTest(TestCase):

    def setUp(self):
        self.a_user = User.objects.create_user(username='legat', email='legat@localhost', password='top_secret')
        self.a_person = test_person.create_person_with_user(self.a_user)
        Group.objects.get_or_create(name='tutors')
        self.a_tutor = test_tutor.create_tutor_with_person(self.a_person)
        self.a_current_academic_yr = test_academic_year.create_academic_year_with_year(CURRENT_YEAR)
        self.a_learning_unit_year = test_learning_unit_year.create_learning_unit_year({
            'acronym': ACRONYM,
            'title': TITLE,
            'academic_year': self.a_current_academic_yr,
            'weight': WEIGHT})
        self.a_learning_unit_component_lecture = test_learning_unit_component.create_learning_unit_component({
            'learning_unit_year': self.a_learning_unit_year,
            'type': component_type.LECTURING,
            'duration': LEARNING_UNIT_LECTURING_DURATION})
        self.a_learning_unit_component_practice = \
            test_learning_unit_component.create_learning_unit_component({
                'learning_unit_year': self.a_learning_unit_year,
                'type': component_type.PRACTICAL_EXERCISES,
                'duration': LEARNING_UNIT_PRACTICAL_EXERCISES_DURATION})
        self.a_tutor_application = test_tutor_application.create_tutor_application(
            {'function': function.CO_HOLDER,
             'tutor': self.a_tutor,
             'learning_unit_year': self.a_learning_unit_year})

        self.an_application_charge_lecturing = test_application_charge.create_application_charge(
            {'tutor_application': self.a_tutor_application,
             'learning_unit_component': self.a_learning_unit_component_lecture,
             'allocation_charge': 15})
        self.an_application_charge_practical = test_application_charge.create_application_charge(
            {'tutor_application': self.a_tutor_application,
             'learning_unit_component': self.a_learning_unit_component_practice,
             'allocation_charge': 20})

    def test_creation_message_from_application_charge(self):
        try:
            generating_message.generate_message_from_application_charge(self.an_application_charge_lecturing, 'update')
        except Exception:
            self.fail("{0} raised ExceptionType unexpectedly!"
                      .format("test_creation_message_from_application_charge"))

    def test_creation_message_from_application_charge_with_unexpected_external_id_format(self):
        try:
            self.an_application_charge_lecturing.learning_unit_component.learning_unit_year.external_id = '428750.2017'
            generating_message.generate_message_from_application_charge(self.an_application_charge_lecturing, 'update')
        except Exception:
            self.fail("{0} raised ExceptionType unexpectedly!"
                      .format("test_creation_message_from_application_charge"))

    def test_get_allocation_charge_with_no_component_type_define(self):
        self.assertEqual(generating_message.get_allocation_charge(self.a_tutor_application, None), CHARGE_NULL)
