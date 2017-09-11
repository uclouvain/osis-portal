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

from unittest import mock

from django.contrib.auth.models import User, Group
from django.test import TestCase
from django.conf import settings

from attribution.views import tutor_charge
from base.models.enums import component_type
from attribution.models.enums import function
from performance.tests.models import test_student_performance
from base.tests.models import test_person, test_tutor, test_academic_year, test_learning_unit_year, \
    test_learning_unit_component
from attribution.tests.models import test_attribution_charge, test_attribution


REGISTRATION_ID = '64641200'

LEARNING_UNIT_LECTURING_DURATION = 15.0
LEARNING_UNIT_PRACTICAL_EXERCISES_DURATION = 30.0
LEARNING_UNIT_CHARGE = 60.0

ATTRIBUTION_CHARGE_LECTURING_DURATION = 15.0
ATTRIBUTION_CHARGE_PRACTICAL_EXERCISES_DURATION = 15.0

ACRONYM = 'LELEC1530'
TITLE = 'Circ. Electro. Analog. & Digit. Fondam.'
WEIGHT = 5
now = datetime.datetime.now()
CURRENT_YEAR = now.year
NEXT_YEAR = now.year + 1
LEARNING_UNIT_ID = "8080"
EXTERNAL_ID = "osis.learning_unit_year_{learning_unit_id}_{year}".format(learning_unit_id=LEARNING_UNIT_ID,
    year=CURRENT_YEAR)

def mock_request_attributions_charge(*args, **kwargs):
    class MockRequest:
        status_code = 200

        def json(self):
            return {"tutorAllocations": [
                {"allocationChargeLecturing":str(LEARNING_UNIT_LECTURING_DURATION),
                 "allocationChargePractice":str(LEARNING_UNIT_PRACTICAL_EXERCISES_DURATION),
                 "learningUnitCharge": str(LEARNING_UNIT_CHARGE),
                 "function":"COORDINATOR",
                 "globalId":"00233751",
                 "learningUnitId":str(LEARNING_UNIT_ID),
                 "year":str(CURRENT_YEAR)}
            ]}
    return MockRequest()

class TutorChargeTest(TestCase):

    def setUp(self):
        self.init_data()

    def init_data(self):
        self.create_tutor()
        self.data = []
        self.data.append(self.create_lu_yr_annual_data(CURRENT_YEAR))
        self.data.append(self.create_lu_yr_annual_data(NEXT_YEAR))
        Group.objects.get_or_create(name='students')

    def create_lu_yr_annual_data(self, a_year):
        an_academic_yr = test_academic_year.create_academic_year_with_year(a_year)
        an_academic_yr.year = a_year
        a_learning_unit_year = test_learning_unit_year.create_learning_unit_year({
            'external_id': EXTERNAL_ID,
            'acronym': ACRONYM,
            'title': TITLE,
            'academic_year': an_academic_yr,
            'weight': WEIGHT,
            'vacant': True,
            'in_charge': True})
        a_learning_unit_component_lecture = self.create_learning_unit_component(component_type.LECTURING,
                                                                                LEARNING_UNIT_LECTURING_DURATION,
                                                                                a_learning_unit_year)
        a_learning_unit_component_practice = \
            self.create_learning_unit_component(component_type.PRACTICAL_EXERCISES,
                                                LEARNING_UNIT_PRACTICAL_EXERCISES_DURATION,
                                                a_learning_unit_year)
        an_attribution = test_attribution.create_attribution({'function': function.CO_HOLDER,
                                                              'learning_unit_year': a_learning_unit_year,
                                                              'tutor': self.a_tutor})
        test_attribution_charge.create_attribution_charge(
            {'attribution': an_attribution,
             'learning_unit_component': a_learning_unit_component_lecture,
             'allocation_charge': ATTRIBUTION_CHARGE_LECTURING_DURATION})
        test_attribution_charge.create_attribution_charge(
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
        self.a_person = test_person.create_person_with_user(self.a_user)
        Group.objects.get_or_create(name='tutors')
        self.a_tutor = test_tutor.create_tutor_with_person(self.a_person)

    def create_learning_unit_component(self, a_component_type, duration, a_learning_unit_year):
        return test_learning_unit_component.create_learning_unit_component({
            'learning_unit_year': a_learning_unit_year,
            'type': a_component_type,
            'duration': duration})

    def create_user(self, username, email, password):
        return User.objects.create_user(username, email, password)

    def calculate_formatted_percentage(self):
        tot_allocation_charge = ATTRIBUTION_CHARGE_LECTURING_DURATION + ATTRIBUTION_CHARGE_PRACTICAL_EXERCISES_DURATION
        tot_learning_unit_duration = LEARNING_UNIT_LECTURING_DURATION + LEARNING_UNIT_PRACTICAL_EXERCISES_DURATION
        percentange_expected = tot_allocation_charge * 100 / tot_learning_unit_duration
        return tutor_charge.ONE_DECIMAL_FORMAT % (percentange_expected,)

    def create_learning_unit_year_without_duration(self):
        a_learning_unit_year_without_duration = test_learning_unit_year.create_learning_unit_year({
            'acronym': ACRONYM,
            'title': TITLE,
            'academic_year': test_academic_year.create_academic_year_with_year(2016)})
        return a_learning_unit_year_without_duration

    def test_get_person_from_user(self):
        self.assertEqual(tutor_charge.get_person(self.a_user), self.a_person)

    def test_get_non_existing_person_from_user(self):
        a_user_not_known = self.create_user('jacobette', 'jacobette@localhost', 'top_secret')
        self.assertIsNone(tutor_charge.get_person(a_user_not_known))

    def get_data(self, key):
        data_year = self.data[0]
        return data_year.get(key, None)

    def test_get_attribution_charge_lecturing_duration(self):
        self.assertEqual(tutor_charge.attribution_allocation_charges(self.a_tutor,
                                                                     self.get_data('learning_unit_year'),
                                                                     component_type.LECTURING),
                         ATTRIBUTION_CHARGE_LECTURING_DURATION)

    def test_get_attribution_charge_practice_exercises_duration(self):
        self.assertEqual(tutor_charge.attribution_allocation_charges(self.a_tutor,
                                                                     self.get_data('learning_unit_year'),
                                                                     component_type.PRACTICAL_EXERCISES),
                         ATTRIBUTION_CHARGE_PRACTICAL_EXERCISES_DURATION)

    def test_sum_learning_unit_year_duration(self):
        self.assertEqual(tutor_charge.sum_learning_unit_year_duration(self.get_data('learning_unit_year')),
                         LEARNING_UNIT_LECTURING_DURATION + LEARNING_UNIT_PRACTICAL_EXERCISES_DURATION)

    def test_sum_learning_unit_year_with_no_duration(self):
        self.assertEqual(tutor_charge.sum_learning_unit_year_duration(self.create_learning_unit_year_without_duration()), 0)

    def test_calculate_percentage_allocation_charge(self):
        self.assertEqual(tutor_charge.calculate_attribution_format_percentage_allocation_charge(
            LEARNING_UNIT_LECTURING_DURATION, LEARNING_UNIT_PRACTICAL_EXERCISES_DURATION, LEARNING_UNIT_CHARGE), "75.0")

    def test_calculate_percentage_allocation_charge_with_no_duration(self):
        self.assertIsNone(tutor_charge.calculate_attribution_format_percentage_allocation_charge(
            LEARNING_UNIT_LECTURING_DURATION, LEARNING_UNIT_PRACTICAL_EXERCISES_DURATION, 0))

    def test_format_students_email(self):
        email_expected = "{0}{1}{2}".format(tutor_charge.MAIL_TO, ACRONYM.lower(), tutor_charge.STUDENT_LIST_EMAIL_END)
        self.assertEqual(tutor_charge.get_email_students(ACRONYM), email_expected)

    def test_format_students_email_without_acronym(self):
        self.assertIsNone(tutor_charge.get_email_students(None))

    def test_get_schedule_url(self):
        url_expected = settings.ATTRIBUTION_CONFIG.get('TIME_TABLE_URL').\
            format(settings.ATTRIBUTION_CONFIG.get('TIME_TABLE_NUMBER'), ACRONYM.lower())
        self.assertEqual(tutor_charge.get_schedule_url(ACRONYM), url_expected)

    def test_get_schedule_url_without_acronym(self):
        self.assertIsNone(tutor_charge.get_schedule_url(None))

    def test_list_attributions(self):
        list_attributions = [self.get_data('attribution')]
        self.assertEqual(list(tutor_charge.list_attributions(self.a_person, self.get_data('academic_year'))),
                         list_attributions)

    def test_attribution_years(self):
        list_years = [NEXT_YEAR, CURRENT_YEAR]
        self.assertEqual(tutor_charge.get_attribution_years(self.a_person), list_years)

    def test_get_url_learning_unit_year(self):
        a_learning_unit_year = self.get_data('learning_unit_year')
        url_learning_unit = settings.ATTRIBUTION_CONFIG.get('CATALOG_URL').format(a_learning_unit_year.academic_year.year,
                                                                                  ACRONYM.lower())
        self.assertEqual(tutor_charge.get_url_learning_unit_year(a_learning_unit_year), url_learning_unit)

    def test_find_january_note(self):
        student_performance = test_student_performance.create_student_performance()
        an_academic_yr = test_academic_year.create_academic_year_with_year(student_performance.academic_year)
        a_learning_unit_year = test_learning_unit_year.create_learning_unit_year({
            'acronym': 'LINGI2145',
            'title': TITLE,
            'academic_year': an_academic_yr,
            'weight': WEIGHT})
        self.assertEqual(tutor_charge.get_sessions_results(student_performance.registration_id,
                                                           a_learning_unit_year,
                                                           student_performance.acronym)
                         , {tutor_charge.JANUARY:
                                {tutor_charge.JSON_LEARNING_UNIT_NOTE: '13.0',
                                 tutor_charge.JSON_LEARNING_UNIT_STATUS: 'I'},
                            tutor_charge.JUNE:
                                {tutor_charge.JSON_LEARNING_UNIT_NOTE: '13.0',
                                 tutor_charge.JSON_LEARNING_UNIT_STATUS: 'R'},
                            tutor_charge.SEPTEMBER:
                                {tutor_charge.JSON_LEARNING_UNIT_NOTE: '-',
                                 tutor_charge.JSON_LEARNING_UNIT_STATUS: '-'}})

    def test_get_student_performance_data_dict(self):
        student_performance = test_student_performance.create_student_performance()
        self.assertEqual(tutor_charge.get_student_data_dict(student_performance), student_performance.data)

    def test_get_no_student_performance_data_dict(self):
        self.assertIsNone(tutor_charge.get_student_data_dict(None))

    def test_no_current_academic_year(self):
        a_year = datetime.datetime.now().year
        self.assertEqual(tutor_charge.get_current_academic_year(), a_year)

    def test_string_none(self):
        self.assertFalse(tutor_charge.is_string_not_null_empty(None))

    def test_string_empty(self):
        self.assertFalse(tutor_charge.is_string_not_null_empty(""))

    def test_string_not_empty(self):
        self.assertTrue(tutor_charge.is_string_not_null_empty("test"))

    @mock.patch('requests.get', side_effect=Exception)
    def test_get_attributions_charge_duration(self, mock_requests_get):
        attributions_charge = tutor_charge.get_attributions_charge_duration(self.a_tutor.person,
                                                                            self.get_data('academic_year'))
        self.assertTrue(mock_requests_get.called)
        self.assertEqual(attributions_charge, {})

    @mock.patch('requests.get', side_effect=mock_request_attributions_charge)
    def test_list_teaching_charge(self, mock_requests_get):
        teaching_charge = tutor_charge.list_teaching_charge(self.a_tutor.person, self.get_data('academic_year'))

        self.assertTrue(mock_requests_get.called)

        attributions = teaching_charge["attributions"]
        tot_lecturing = teaching_charge["tot_lecturing"]
        tot_practical = teaching_charge["tot_practical"]

        self.assertEqual(len(attributions), 1)
        self.assertEqual(attributions[0]["lecturing_allocation_charge"], str(LEARNING_UNIT_LECTURING_DURATION))
        self.assertEqual(attributions[0]["practice_allocation_charge"], str(LEARNING_UNIT_PRACTICAL_EXERCISES_DURATION))
        self.assertEqual(attributions[0]["percentage_allocation_charge"], "75.0")
        self.assertEqual(tot_lecturing, LEARNING_UNIT_LECTURING_DURATION)
        self.assertEqual(tot_practical, LEARNING_UNIT_PRACTICAL_EXERCISES_DURATION)
