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
from attribution.views import online_application, teaching_load
from base.models.enums import component_type
from base.tests.models import test_person, test_tutor,test_academic_year, test_learning_unit_year, test_learning_unit_component
from attribution.tests.models import test_attribution_charge, test_attribution
from attribution.models.enums import function

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
        a_current_academic_yr = test_academic_year.create_academic_year_with_year(CURRENT_YEAR)
        a_next_academic_yr = test_academic_year.create_academic_year_with_year(NEXT_YEAR)
        start = PREVIOUS_YEAR
        end = NEXT_YEAR
        self.learning_unit_year1_previous = self.create_learning_unit_year_annual_data(ACRONYM, TITLE, a_previous_academic_yr)
        self.learning_unit_year1_current = self.create_learning_unit_year_annual_data(ACRONYM, TITLE, a_current_academic_yr)
        self.learning_unit_year1_next = self.create_learning_unit_year_annual_data(ACRONYM, TITLE, a_next_academic_yr)
        self.learning_unit_year1_previous = self.create_learning_unit_year_annual_data(ACRONYM2, TITLE2, a_previous_academic_yr)
        self.learning_unit_year1_current = self.create_learning_unit_year_annual_data(ACRONYM2, TITLE2, a_current_academic_yr)
        self.learning_unit_year1_next = self.create_learning_unit_year_annual_data(ACRONYM2, TITLE2, a_next_academic_yr)

    def create_learning_unit_year_annual_data(self, an_acronym, a_title, an_academic_yr):
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
        an_attribution = test_attribution.create_attribution({'function': function.CO_HOLDER,
                                                              'learning_unit_year': a_learning_unit_year,
                                                              'tutor': self.a_tutor,
                                                              'start': START,
                                                              'end': END})
        test_attribution_charge.create_attribution_charge(
            {'attribution': an_attribution,
             'learning_unit_component': a_learning_unit_component_lecture,
             'allocation_charge': ATTRIBUTION_CHARGE_LECTURING_DURATION})
        test_attribution_charge.create_attribution_charge(
            {'attribution': an_attribution,
             'learning_unit_component': a_learning_unit_component_practice,
             'allocation_charge': ATTRIBUTION_CHARGE_PRACTICAL_EXERCISES_DURATION})

        return a_learning_unit_year


    def test_get_learning_unit_component_duration(self):
        self.assertEqual(online_application.get_learning_unit_component_duration(self.learning_unit_year1_current, component_type.LECTURING), LEARNING_UNIT_LECTURING_DURATION)


    def test_get_current_attributions(self):

        data1 = {online_application.ACRONYM:                      ACRONYM,
                 online_application.TITLE:                        TITLE,
                 online_application.LECTURING_DURATION:           online_application.TWO_DECIMAL_FORMAT % (LEARNING_UNIT_LECTURING_DURATION,),
                 online_application.PRACTICAL_DURATION:           online_application.TWO_DECIMAL_FORMAT % (LEARNING_UNIT_PRACTICAL_EXERCISES_DURATION,),
                 online_application.START:                        START,
                 online_application.END:                          END,
                 online_application.ATTRIBUTION_CHARGE_LECTURING: online_application.TWO_DECIMAL_FORMAT % (ATTRIBUTION_CHARGE_LECTURING_DURATION,),
                 online_application.ATTRIBUTION_CHARGE_PRACTICAL: online_application.TWO_DECIMAL_FORMAT % (ATTRIBUTION_CHARGE_PRACTICAL_EXERCISES_DURATION,),
                 online_application.FUNCTION:                     function.CO_HOLDER
        }
        data2 = {online_application.ACRONYM:                      ACRONYM2,
                 online_application.TITLE:                        TITLE2,
                 online_application.LECTURING_DURATION:           online_application.TWO_DECIMAL_FORMAT % (LEARNING_UNIT_LECTURING_DURATION,),
                 online_application.PRACTICAL_DURATION:           online_application.TWO_DECIMAL_FORMAT % (LEARNING_UNIT_PRACTICAL_EXERCISES_DURATION,),
                 online_application.START:                        START,
                 online_application.END:                          END,
                 online_application.ATTRIBUTION_CHARGE_LECTURING: online_application.TWO_DECIMAL_FORMAT % (ATTRIBUTION_CHARGE_LECTURING_DURATION,),
                 online_application.ATTRIBUTION_CHARGE_PRACTICAL: online_application.TWO_DECIMAL_FORMAT % (ATTRIBUTION_CHARGE_PRACTICAL_EXERCISES_DURATION,),
                 online_application.FUNCTION:                     function.CO_HOLDER
               }
        data = [data1, data2]

        self.assertEqual(online_application.get_attributions_allocated(CURRENT_YEAR, self.a_tutor), data)
