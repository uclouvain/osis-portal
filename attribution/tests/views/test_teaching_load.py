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
from django.conf import settings

import admission.tests.data_for_tests as data_model
from attribution.views import teaching_load
from base.models.enums import component_type
from attribution.models.enums import function

LEARNING_UNIT_LECTURING_DURATION = 15.00
LEARNING_UNIT_PRACTICAL_EXERCISES_DURATION = 30.00

ATTRIBUTION_CHARGE_LECTURING_DURATION = 15.00
ATTRIBUTION_CHARGE_PRACTICAL_EXERCISES_DURATION = 15.00

ACRONYM = 'LELEC1530'
TITLE = 'Circ. Electro. Analog. & Digit. Fondam.'
WEIGHT = 5
now = datetime.datetime.now()
CURRENT_YEAR = now.year
NEXT_YEAR = now.year + 1


class TeachingLoadTest(TestCase):

    def setUp(self):
        self.init_data()

    def init_data(self):
        self.create_tutor()
        self.data = []
        self.data.append(self.create_learning_unit_year_annual_data(CURRENT_YEAR))
        self.data.append(self.create_learning_unit_year_annual_data(NEXT_YEAR))

    def create_learning_unit_year_annual_data(self, a_year):
        an_academic_yr = data_model.create_academic_year_with_year(a_year)
        an_academic_yr.year = a_year
        a_learning_unit_year = data_model.create_learning_unit_year({
            'acronym': ACRONYM,
            'title': TITLE,
            'academic_year': an_academic_yr,
            'weight': WEIGHT})
        a_learning_unit_component_lecture = self.create_learning_unit_component(component_type.LECTURING,
                                                                                LEARNING_UNIT_LECTURING_DURATION,
                                                                                a_learning_unit_year)
        a_learning_unit_component_practice = \
            self.create_learning_unit_component(component_type.PRACTICAL_EXERCISES,
                                                LEARNING_UNIT_PRACTICAL_EXERCISES_DURATION,
                                                a_learning_unit_year)
        an_attribution = data_model.create_attribution({'function': function.CO_HOLDER,
                                                        'learning_unit_year': a_learning_unit_year,
                                                        'tutor': self.a_tutor})
        data_model.create_attribution_charge(
            {'attribution': an_attribution,
             'learning_unit_component': a_learning_unit_component_lecture,
             'allocation_charge': ATTRIBUTION_CHARGE_LECTURING_DURATION})
        data_model.create_attribution_charge(
            {'attribution': an_attribution,
             'learning_unit_component': a_learning_unit_component_practice,
             'allocation_charge': ATTRIBUTION_CHARGE_PRACTICAL_EXERCISES_DURATION})

        return {'academic_year':                   an_academic_yr,
                'learning_unit_year':               a_learning_unit_year,
                'learning_unit_component_lecture':  a_learning_unit_component_lecture,
                'learning_unit_component_practice': a_learning_unit_component_practice,
                'attribution':                      an_attribution}

    def create_tutor(self):
        self.a_user = self.create_user(username='jacob', email='jacob@localhost', password='top_secret')
        self.a_person = data_model.create_person(self.a_user)
        Group.objects.get_or_create(name='tutors')
        self.a_tutor = data_model.create_tutor(self.a_person)

    def create_learning_unit_component(self, a_component_type, duration, a_learning_unit_year):
        return data_model.create_learning_unit_component({
            'learning_unit_year': a_learning_unit_year,
            'type': a_component_type,
            'duration': duration})

    def create_user(self, username, email, password):
        return User.objects.create_user(username, email, password)

    def calculate_formatted_percentage(self):
        tot_allocation_charge = ATTRIBUTION_CHARGE_LECTURING_DURATION + ATTRIBUTION_CHARGE_PRACTICAL_EXERCISES_DURATION
        tot_learning_unit_duration = LEARNING_UNIT_LECTURING_DURATION + LEARNING_UNIT_PRACTICAL_EXERCISES_DURATION
        percentange_expected = tot_allocation_charge * 100 / tot_learning_unit_duration
        return "%0.2f" % (percentange_expected,)

    def create_learning_unit_year_without_duration(self):
        a_learning_unit_year_without_duration = data_model.create_learning_unit_year({
            'acronym': ACRONYM,
            'title': TITLE,
            'academic_year': data_model.create_academic_year_with_year(2016)})
        return a_learning_unit_year_without_duration

    def test_get_person_from_user(self):
        self.assertEqual(teaching_load.get_person(self.a_user), self.a_person)

    def test_get_non_existing_person_from_user(self):
        a_user_not_known = self.create_user('jacobette', 'jacobette@localhost', 'top_secret')
        self.assertIsNone(teaching_load.get_person(a_user_not_known))

    def get_data(self, key):
        data_year = self.data[0]
        return data_year.get(key, None)

    def test_get_title(self):
        self.assertEqual(teaching_load.get_title_uppercase(self.get_data('learning_unit_year')), TITLE.upper())

    def test_get_title_non_existing_learning_unit_year(self):
        self.assertEqual(teaching_load.get_title_uppercase(None), '')

    def test_get_title_non_existing_title(self):
        a_learning_unit_year_without_title = self.get_data('learning_unit_year')
        a_learning_unit_year_without_title.title = None
        self.assertEqual(teaching_load.get_title_uppercase(a_learning_unit_year_without_title), '')

    def test_get_attribution_charge_lecturing_duration(self):
        self.assertEqual(teaching_load.get_attribution_allocation_charge(self.a_tutor,
                                                                         self.get_data('learning_unit_year'),
                                                                         component_type.LECTURING), ATTRIBUTION_CHARGE_LECTURING_DURATION)

    def test_get_attribution_charge_practice_exercises_duration(self):
        self.assertEqual(teaching_load.get_attribution_allocation_charge(self.a_tutor,
                                                                         self.get_data('learning_unit_year'),
                                                                         component_type.PRACTICAL_EXERCISES), ATTRIBUTION_CHARGE_PRACTICAL_EXERCISES_DURATION)

    def test_sum_learning_unit_year_duration(self):
        self.assertEqual(teaching_load.sum_learning_unit_year_duration(self.get_data('learning_unit_year')), LEARNING_UNIT_LECTURING_DURATION + LEARNING_UNIT_PRACTICAL_EXERCISES_DURATION)

    def test_sum_learning_unit_year_with_no_duration(self):
        self.assertEqual(teaching_load.sum_learning_unit_year_duration(self.create_learning_unit_year_without_duration()), 0)

    def test_sum_learning_unit_year_allocation_charg(self):
        self.assertEqual(teaching_load.sum_learning_unit_year_allocation_charge(self.a_tutor, self.get_data('learning_unit_year')), ATTRIBUTION_CHARGE_LECTURING_DURATION + ATTRIBUTION_CHARGE_PRACTICAL_EXERCISES_DURATION)

    def test_calculate_percentage_allocation_charge(self):
        self.assertEqual(teaching_load.calculate_format_percentage_allocation_charge(self.a_tutor, self.get_data('learning_unit_year')), self.calculate_formatted_percentage())

    def test_calculate_percentage_allocation_charge_with_no_duration(self):
        self.assertIsNone(teaching_load.calculate_format_percentage_allocation_charge(self.a_tutor,
                                                                                      self.create_learning_unit_year_without_duration()))

    def test_format_students_email(self):
        email_expected = "{0}{1}{2}".format(teaching_load.MAIL_TO, ACRONYM.lower(), teaching_load.STUDENT_LIST_EMAIL_END)
        self.assertEqual(teaching_load.get_email_students(ACRONYM), email_expected)

    def test_format_students_email_without_acronym(self):
        self.assertIsNone(teaching_load.get_email_students(None))

    def test_get_schedule_url(self):
        url_expected = settings.ADE_MAIN_URL.format(settings.ADE_PROJET_NUMBER, ACRONYM.lower())
        self.assertEqual(teaching_load.get_schedule_url(ACRONYM), url_expected)

    def test_get_schedule_url_without_acronym(self):
        self.assertIsNone(teaching_load.get_schedule_url(None))

    def test_list_attributions(self):
        list_attributions = [self.get_data('attribution')]
        self.assertEqual(list(teaching_load.list_attributions(self.a_person, self.get_data('academic_year'))), list_attributions)

    def test_list_teaching_load_attribution_representation(self):
        list_attributions = []
        a_learning_unit_year = self.get_data('learning_unit_year')
        teaching_load_attribution_representation = {
            'acronym' :a_learning_unit_year.acronym,
            'title': TITLE.upper(),
            'lecturing_allocation_charge': "%0.2f" % (ATTRIBUTION_CHARGE_LECTURING_DURATION,),
            'practice_allocation_charge': "%0.2f" % (ATTRIBUTION_CHARGE_PRACTICAL_EXERCISES_DURATION,),
            'percentage_allocation_charge': self.calculate_formatted_percentage(),
            'weight': a_learning_unit_year.weight,
            'url_schedule': settings.ADE_MAIN_URL.format(settings.ADE_PROJET_NUMBER, ACRONYM.lower()),
            'url_students_list_email': "{0}{1}{2}".format(teaching_load.MAIL_TO,
                                                          ACRONYM.lower(),
                                                          teaching_load.STUDENT_LIST_EMAIL_END),
            'function': self.get_data('attribution').function,
            'year': a_learning_unit_year.academic_year.year}
        list_attributions.append(teaching_load_attribution_representation)
        self.assertEqual(teaching_load.list_teaching_load_attribution_representation(self.a_person, a_learning_unit_year.academic_year), list_attributions)

    def test_attribution_years(self):
        list_years = [NEXT_YEAR, CURRENT_YEAR]
        self.assertEqual(teaching_load.get_attribution_years(self.a_person), list_years)
