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

from attribution.views import teaching_load
from base.models.enums import component_type
from attribution.models.enums import function
from performance.tests.models import test_student_performance
from base.tests.models import test_person, test_tutor, test_academic_year, test_learning_unit_year, \
    test_learning_unit_component, test_offer_enrollment, test_learning_unit_enrollment, test_offer_year, test_student
from attribution.tests.models import test_attribution_charge, test_attribution


REGISTRATION_ID = '64641200'

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
        Group.objects.get_or_create(name='students')

    def create_learning_unit_year_annual_data(self, a_year):
        an_academic_yr = test_academic_year.create_academic_year_with_year(a_year)
        an_academic_yr.year = a_year
        a_learning_unit_year = test_learning_unit_year.create_learning_unit_year({
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
        return teaching_load.ONE_DECIMAL_FORMAT % (percentange_expected,)

    def create_learning_unit_year_without_duration(self):
        a_learning_unit_year_without_duration = test_learning_unit_year.create_learning_unit_year({
            'acronym': ACRONYM,
            'title': TITLE,
            'academic_year': test_academic_year.create_academic_year_with_year(2016)})
        return a_learning_unit_year_without_duration

    def create_student(self, cpt):
        a_student_user = self.create_user(username='student{0}'.format(cpt),
                                          email='student{0}@localhost'.format(cpt),
                                          password='top_student')
        return test_student.create_student_with_registration_person(cpt, test_person.create_person_with_user(a_student_user))

    def test_get_person_from_user(self):
        self.assertEqual(teaching_load.get_person(self.a_user), self.a_person)

    def test_get_non_existing_person_from_user(self):
        a_user_not_known = self.create_user('jacobette', 'jacobette@localhost', 'top_secret')
        self.assertIsNone(teaching_load.get_person(a_user_not_known))

    def get_data(self, key):
        data_year = self.data[0]
        return data_year.get(key, None)

    def create_student_performance(a_learning_unit_year):
        with open("performance/tests/ressources/points.json") as f:
            data = json.load(f)

        a_student_performance = mdl_performance.student_performance.StudentPerformance(acronym=ACRONYM,
                                                                                       registration_id=REGISTRATION_ID,
                                                                                       academic_year=a_learning_unit_year.academic_year.year,
                                                                                       update_date=datetime.datetime.now(),
                                                                                       data=data)
        a_student_performance.save()
        return a_student_performance

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
            'acronym': a_learning_unit_year.acronym,
            'title': TITLE.upper(),
            'lecturing_allocation_charge': teaching_load.ONE_DECIMAL_FORMAT % (ATTRIBUTION_CHARGE_LECTURING_DURATION,),
            'practice_allocation_charge': teaching_load.ONE_DECIMAL_FORMAT % (ATTRIBUTION_CHARGE_PRACTICAL_EXERCISES_DURATION,),
            'percentage_allocation_charge': self.calculate_formatted_percentage(),
            'weight': a_learning_unit_year.weight,
            'url_schedule': settings.ADE_MAIN_URL.format(settings.ADE_PROJET_NUMBER, ACRONYM.lower()),
            'url_students_list_email': "{0}{1}{2}".format(teaching_load.MAIL_TO,
                                                          ACRONYM.lower(),
                                                          teaching_load.STUDENT_LIST_EMAIL_END),
            'function': self.get_data('attribution').function,
            'year': a_learning_unit_year.academic_year.year,
            'learning_unit_year_url': settings.UCL_URL.format(a_learning_unit_year.academic_year.year, ACRONYM.lower()),
            'learning_unit_year': a_learning_unit_year}
        list_attributions.append(teaching_load_attribution_representation)
        self.assertEqual(teaching_load.list_teaching_load_attribution_representation(self.a_person, a_learning_unit_year.academic_year), list_attributions)

    def test_attribution_years(self):
        list_years = [NEXT_YEAR, CURRENT_YEAR]
        self.assertEqual(teaching_load.get_attribution_years(self.a_person), list_years)

    def test_get_url_learning_unit_year(self):
        a_learning_unit_year = self.get_data('learning_unit_year')
        url_learning_unit = settings.UCL_URL.format(a_learning_unit_year.academic_year.year, ACRONYM.lower())
        self.assertEqual(teaching_load.get_url_learning_unit_year(a_learning_unit_year), url_learning_unit)

    def test_find_enrollments(self):
        a_learning_unit_year = self.get_data('learning_unit_year')
        list_learning_unit_enrollment = []
        offer_year = test_offer_year.create_offer_year()
        i = 0
        while i < 5:
            student1 = self.create_student(i)
            offer_enrollment = test_offer_enrollment\
                .create_offer_enrollment_with_academic_year(offer_year, student1, a_learning_unit_year.academic_year)
            learning_unit_enrollment = test_learning_unit_enrollment\
                .create_learning_unit_enrollment(offer_enrollment, a_learning_unit_year)
            list_learning_unit_enrollment.append(learning_unit_enrollment)
            i = i + 1

        self.assertEqual(list(teaching_load.get_students(a_learning_unit_year)), list_learning_unit_enrollment)

    def test_find_january_note(self):
        student_performance = test_student_performance.create_student_performance()
        an_academic_yr = test_academic_year.create_academic_year_with_year(student_performance.academic_year)
        a_learning_unit_year = test_learning_unit_year.create_learning_unit_year({
            'acronym': 'LINGI2145',
            'title': TITLE,
            'academic_year': an_academic_yr,
            'weight': WEIGHT})
        self.assertEqual(teaching_load.get_sessions_results(student_performance.registration_id,
                                                            a_learning_unit_year,
                                                            student_performance.acronym)
                         , {teaching_load.JANUARY:
                                {teaching_load.JSON_LEARNING_UNIT_NOTE: '13.0',
                                 teaching_load.JSON_LEARNING_UNIT_STATUS: 'I'},
                            teaching_load.JUNE:
                                {teaching_load.JSON_LEARNING_UNIT_NOTE: '13.0',
                                 teaching_load.JSON_LEARNING_UNIT_STATUS: 'R'},
                            teaching_load.SEPTEMBER:
                                {teaching_load.JSON_LEARNING_UNIT_NOTE: '-',
                                 teaching_load.JSON_LEARNING_UNIT_STATUS: '-'}})

    def test_get_student_performance_data_dict(self):
        student_performance = test_student_performance.create_student_performance()
        self.assertEqual(teaching_load.get_student_data_dict(student_performance), student_performance.data)

    def test_get_no_student_performance_data_dict(self):
        self.assertIsNone(teaching_load.get_student_data_dict(None))
