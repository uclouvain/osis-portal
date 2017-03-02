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
from attribution.views import online_application
from base.models.enums import component_type
from base.tests.models import test_person, test_tutor, test_academic_year, test_learning_unit_year, \
    test_learning_unit_component, test_learning_unit
from attribution.tests.models import test_attribution_charge, test_attribution, test_application_charge, test_tutor_application
from attribution.models.enums import function
from base import models as mdl_base


now = datetime.datetime.now()

PREVIOUS_YEAR = now.year - 1
CURRENT_YEAR = now.year
NEXT_YEAR = now.year + 1


LEARNING_UNIT_LECTURING_DURATION = 15.00
LEARNING_UNIT_PRACTICAL_EXERCISES_DURATION = 30.00

ATTRIBUTION_CHARGE_LECTURING_DURATION = 15.00
ATTRIBUTION_CHARGE_PRACTICAL_EXERCISES_DURATION = 15.00

ACRONYM = 'LFSAB1003'
TITLE = 'METHODES NUMERIQUES'

ACRONYM2 = 'LFSAB1104'
TITLE2 = 'Coordination du quadrimestre 3'

ACRONYM_VACANT_LEARNING_UNIT = 'LFSAB1105'
TITLE_VACANT_LEARNING_UNIT = 'Coordination et mathématiques'

WEIGHT = 5

START = PREVIOUS_YEAR
END = NEXT_YEAR


class OnlineApplicationTest(TestCase):

    def setUp(self):
        self.a_user = User.objects.create_user(username='legat', email='legat@localhost', password='top_secret')
        self.a_person = test_person.create_person_with_user(self.a_user)
        Group.objects.get_or_create(name='tutors')
        self.a_tutor = test_tutor.create_tutor_with_person(self.a_person)
        a_previous_academic_yr = test_academic_year.create_academic_year_with_year(PREVIOUS_YEAR)
        self.a_current_academic_yr = test_academic_year.create_academic_year_with_year(CURRENT_YEAR)
        a_next_academic_yr = test_academic_year.create_academic_year_with_year(NEXT_YEAR)

        self.learning_unit_year1_partially_vacant_previous = self.create_learning_unit_year_annual_data(ACRONYM, TITLE, a_previous_academic_yr, self.a_tutor, START, END)
        self.learning_unit_year1_partially_vacant_current = self.create_learning_unit_year_annual_data(ACRONYM, TITLE, self.a_current_academic_yr, self.a_tutor, START, END)
        self.learning_unit_year1_partially_vacant_next = self.create_learning_unit_year_annual_data(ACRONYM, TITLE, a_next_academic_yr, self.a_tutor, START, END)
        self.learning_unit_year2_partially_vacant_previous = self.create_learning_unit_year_annual_data(ACRONYM2, TITLE2, a_previous_academic_yr, self.a_tutor, START, END)
        self.learning_unit_year2_partially_vacant_current = self.create_learning_unit_year_annual_data(ACRONYM2, TITLE2, self.a_current_academic_yr, self.a_tutor, START, END)
        self.learning_unit_year2_partially_vacant_next = self.create_learning_unit_year_annual_data(ACRONYM2, TITLE2, a_next_academic_yr, self.a_tutor, START, END)

        self.learning_unit_year_totally_vacant_next = self.create_learning_unit_year_annual_data(ACRONYM_VACANT_LEARNING_UNIT, TITLE_VACANT_LEARNING_UNIT, a_next_academic_yr, None, START, END)

    def create_learning_unit_year_annual_data(self, an_acronym, a_title, an_academic_yr, a_tutor, start, end):
        a_learning_unit_year = test_learning_unit_year.create_learning_unit_year({
            'acronym': an_acronym,
            'title': a_title,
            'academic_year': an_academic_yr,
            'weight': WEIGHT})
        a_learning_unit_component_lecture = test_learning_unit_component.create_learning_unit_component({
            'learning_unit_year': a_learning_unit_year,
            'type': component_type.LECTURING,
            'duration': LEARNING_UNIT_LECTURING_DURATION})
        a_learning_unit_component_practice = \
            test_learning_unit_component.create_learning_unit_component({
                'learning_unit_year': a_learning_unit_year,
                'type': component_type.PRACTICAL_EXERCISES,
                'duration': LEARNING_UNIT_PRACTICAL_EXERCISES_DURATION})
        if a_tutor:
            an_attribution = test_attribution.create_attribution({'function': function.CO_HOLDER,
                                                                  'learning_unit_year': a_learning_unit_year,
                                                                  'tutor': a_tutor,
                                                                  'start_year': start,
                                                                  'end_year': end})
            test_attribution_charge.create_attribution_charge(
                {'attribution': an_attribution,
                 'learning_unit_component': a_learning_unit_component_lecture,
                 'allocation_charge': ATTRIBUTION_CHARGE_LECTURING_DURATION})
            test_attribution_charge.create_attribution_charge(
                {'attribution': an_attribution,
                 'learning_unit_component': a_learning_unit_component_practice,
                 'allocation_charge': ATTRIBUTION_CHARGE_PRACTICAL_EXERCISES_DURATION})

        return a_learning_unit_year

    def get_learning_unit_component(self):
        a_learning_unit_component_practices = mdl_base.learning_unit_component.search(
            self.learning_unit_year1_partially_vacant_next,
            component_type.PRACTICAL_EXERCISES)

        if a_learning_unit_component_practices.exists():
            return a_learning_unit_component_practices[0]
        return None

    def test_get_learning_unit_component_duration(self):
        self.assertEqual(online_application.get_learning_unit_component_duration(self.learning_unit_year1_partially_vacant_current, component_type.LECTURING), LEARNING_UNIT_LECTURING_DURATION)

    def test_get_current_attributions(self):
        unused_year = CURRENT_YEAR+10
        an_new_academic_year = test_academic_year.create_academic_year_with_year(unused_year)
        acronym_1 = 'LMECA2125'
        self.create_learning_unit_year_annual_data(acronym_1, TITLE, an_new_academic_year, self.a_tutor, unused_year, unused_year+1)
        acronym_2 = 'LSTAT8125'
        self.create_learning_unit_year_annual_data(acronym_2, TITLE, an_new_academic_year, self.a_tutor, unused_year, unused_year+1)
        self.assertEqual(len(online_application.get_attributions_allocated(an_new_academic_year.year, self.a_tutor)), 2)

    def test_sum_attribution_allocation_charges(self):
        self.assertEqual(online_application.sum_attribution_allocation_charges(self.learning_unit_year1_partially_vacant_current), ATTRIBUTION_CHARGE_LECTURING_DURATION + ATTRIBUTION_CHARGE_PRACTICAL_EXERCISES_DURATION)

    def test_no_attribution_allocation_charge(self):
        self.assertEqual(online_application.sum_attribution_allocation_charges(self.learning_unit_year_totally_vacant_next), 0)

    def test_get_vacant_attribution_allocation_charge_lecturing(self):
        self.assertEqual(online_application.get_vacant_attribution_allocation_charge(self.learning_unit_year1_partially_vacant_current, component_type.LECTURING), 0)

    def test_get_vacant_attribution_allocation_charge_practical(self):
        self.assertEqual(online_application.get_vacant_attribution_allocation_charge(self.learning_unit_year1_partially_vacant_current, component_type.PRACTICAL_EXERCISES), 15.00)

    def test_get_vacant_learning_units(self):
        data1 = {online_application.ACRONYM:                      ACRONYM,
                 online_application.TITLE:                        TITLE,
                 online_application.LECTURING_DURATION:           LEARNING_UNIT_LECTURING_DURATION,
                 online_application.PRACTICAL_DURATION:           LEARNING_UNIT_PRACTICAL_EXERCISES_DURATION,

                 online_application.VACANT_ATTRIBUTION_CHARGE_LECTURING: LEARNING_UNIT_LECTURING_DURATION-ATTRIBUTION_CHARGE_LECTURING_DURATION,
                 online_application.VACANT_ATTRIBUTION_CHARGE_PRACTICAL: LEARNING_UNIT_PRACTICAL_EXERCISES_DURATION-ATTRIBUTION_CHARGE_PRACTICAL_EXERCISES_DURATION,
                 }

        data2 = {online_application.ACRONYM:                      ACRONYM2,
                 online_application.TITLE:                        TITLE2,
                 online_application.LECTURING_DURATION:           LEARNING_UNIT_LECTURING_DURATION,
                 online_application.PRACTICAL_DURATION:           LEARNING_UNIT_PRACTICAL_EXERCISES_DURATION,

                 online_application.VACANT_ATTRIBUTION_CHARGE_LECTURING: LEARNING_UNIT_LECTURING_DURATION-ATTRIBUTION_CHARGE_LECTURING_DURATION,
                 online_application.VACANT_ATTRIBUTION_CHARGE_PRACTICAL: LEARNING_UNIT_PRACTICAL_EXERCISES_DURATION-ATTRIBUTION_CHARGE_PRACTICAL_EXERCISES_DURATION,

                 }

        data3 = {online_application.ACRONYM:                      ACRONYM_VACANT_LEARNING_UNIT,
                 online_application.TITLE:                        TITLE_VACANT_LEARNING_UNIT,
                 online_application.LECTURING_DURATION:           LEARNING_UNIT_LECTURING_DURATION,
                 online_application.PRACTICAL_DURATION:           LEARNING_UNIT_PRACTICAL_EXERCISES_DURATION,

                 online_application.VACANT_ATTRIBUTION_CHARGE_LECTURING: LEARNING_UNIT_LECTURING_DURATION,
                 online_application.VACANT_ATTRIBUTION_CHARGE_PRACTICAL: LEARNING_UNIT_PRACTICAL_EXERCISES_DURATION,
                 }

        data = [data1, data2, data3]

        self.assertEqual(online_application.get_vacant_learning_units(NEXT_YEAR), data)

    def test_find_no_application(self):
        unexisting_year_date = NEXT_YEAR+100
        self.assertEqual(len(online_application.get_tutor_applications(unexisting_year_date, self.a_tutor)), 0)

    def test_find_applications(self):
        tutor_application_learning_unit_1 = test_tutor_application.create_tutor_application(
            {'function': function.CO_HOLDER,
             'learning_unit_year': self.learning_unit_year1_partially_vacant_next,
             'tutor': self.a_tutor})
        application_charge_duration = LEARNING_UNIT_PRACTICAL_EXERCISES_DURATION - ATTRIBUTION_CHARGE_PRACTICAL_EXERCISES_DURATION
        a_learning_unit_component_practice = self.get_learning_unit_component()
        test_application_charge.create_application_charge(
            {'tutor_application': tutor_application_learning_unit_1,
             'learning_unit_component': a_learning_unit_component_practice,
             'allocation_charge': application_charge_duration})
        self.assertEquals(len(online_application.get_tutor_applications(NEXT_YEAR, self.a_tutor)), 1)

    def test_define_renew_unexisting_academic_year(self):
        a_learning_unit = test_learning_unit.create_learning_unit({'acronym': 'LSTAT2121', 'title': 'Statistiques'})
        a_next_academic_yr = test_academic_year.create_academic_year_with_year(NEXT_YEAR + 10)
        a_learning_unit_year = test_learning_unit_year.create_learning_unit_year({
            'acronym': a_learning_unit.acronym,
            'academic_year': a_next_academic_yr,
            'learning_unit': a_learning_unit})
        self.assertEquals(online_application.define_renew_possible(self.a_tutor, a_learning_unit_year, None), False)

    def test_define_renew_existing_academic_year_true(self):
        a_learning_unit = test_learning_unit.create_learning_unit({'acronym': 'LSTAT2121',
                                                                   'title': 'Statistiques'})
        a_next_academic_yr_plus_4 = test_academic_year.create_academic_year_with_year(NEXT_YEAR + 4)
        a_learning_unit_year_plus_4 = test_learning_unit_year.create_learning_unit_year({
            'acronym': a_learning_unit.acronym,
            'academic_year': a_next_academic_yr_plus_4,
            'learning_unit': a_learning_unit})
        test_learning_unit_year.create_learning_unit_year({
            'acronym': a_learning_unit.acronym,
            'academic_year': test_academic_year.create_academic_year_with_year(NEXT_YEAR + 5),
            'learning_unit': a_learning_unit,
            'vacant': True})
        self.assertEquals(online_application.define_renew_possible(self.a_tutor, a_learning_unit_year_plus_4, None), True)

    def test_define_renew_existing_academic_year_False_already_exists(self):
        a_learning_unit = test_learning_unit.create_learning_unit({'acronym': 'LSTAT2121',
                                                                   'title': 'Statistiques'})
        a_next_academic_yr_plus_4 = test_academic_year.create_academic_year_with_year(NEXT_YEAR + 4)
        a_learning_unit_year_plus_4 = test_learning_unit_year.create_learning_unit_year({
            'acronym': a_learning_unit.acronym,
            'academic_year': a_next_academic_yr_plus_4,
            'learning_unit': a_learning_unit})
        a_next_academic_yr_plus_5 = test_academic_year.create_academic_year_with_year(NEXT_YEAR + 5)
        a_learning_unit_year_plus_5 = test_learning_unit_year.create_learning_unit_year({
            'acronym': a_learning_unit.acronym,
            'academic_year': a_next_academic_yr_plus_5,
            'learning_unit': a_learning_unit})
        test_tutor_application.create_tutor_application({'learning_unit_year': a_learning_unit_year_plus_5,
                                                         'tutor': self.a_tutor,
                                                         'function': function.CO_HOLDER})
        self.assertEquals(online_application.define_renew_possible(self.a_tutor, a_learning_unit_year_plus_4, None), False)

    def test_is_deputy_function(self):
        self.assertEquals(online_application.is_deputy_function(function.DEPUTY_TEMPORARY), True)

    def test_is_not_deputy_function(self):
        self.assertEquals(online_application.is_deputy_function(function.COORDINATOR), False)





