##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2018 Université catholique de Louvain (http://www.uclouvain.be)
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

from requests.exceptions import RequestException
from django.contrib.auth.models import User, Group, Permission
from django.test import TestCase, override_settings
from django.conf import settings
from django.core.urlresolvers import reverse
from django.forms.formsets import BaseFormSet

from attribution.views import tutor_charge
from base.models.enums import component_type
from attribution.models.enums import function
from performance.tests.models import test_student_performance
from base.tests.models import test_person, test_tutor, test_academic_year, test_learning_unit_year, \
    test_learning_unit_component
from base.tests.factories.person import PersonFactory
from base.tests.factories.tutor import TutorFactory
from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.learning_unit_year import LearningUnitYearFactory
from base.tests.factories.learning_container_year import LearningContainerYearFactory
from attribution.tests.factories.attribution import AttributionFactory
from base.models.enums import learning_unit_year_subtypes
from base.tests.factories.learning_unit_enrollment import LearningUnitEnrollmentFactory

URL_ADE = "url_ade"

REGISTRATION_ID = '64641200'

LEARNING_UNIT_LECTURING_DURATION = 15.0
LEARNING_UNIT_PRACTICAL_EXERCISES_DURATION = 30.0
LEARNING_UNIT_CHARGE = 60.0

ATTRIBUTION_CHARGE_LECTURING_DURATION = 15.0
ATTRIBUTION_CHARGE_PRACTICAL_EXERCISES_DURATION = 15.0
ATTRIBUTION_ID = "8080"
ATTRIBUTION_EXTERNAL_ID = "osis.attribution_{attribution_id}".format(attribution_id=ATTRIBUTION_ID)
OTHER_ATTRIBUTION_ID = "8081"
OTHER_ATTRIBUTION_EXTERNAL_ID = "osis.attribution_{attribution_id}".format(attribution_id=OTHER_ATTRIBUTION_ID)

ACRONYM = 'LELEC1530'
TITLE = 'Circ. Electro. Analog. & Digit. Fondam.'
WEIGHT = 5
now = datetime.datetime.now()
CURRENT_YEAR = now.year
NEXT_YEAR = now.year + 1


def get_attribution_config_settings():
    return {'TIME_TABLE_URL': '',
            'TIME_TABLE_NUMBER': '',
            'CATALOG_URL': '',
            'SERVER_TO_FETCH_URL': 'test',
            'ATTRIBUTION_PATH': 'test',
            'SERVER_TO_FETCH_USER': 'test',
            'SERVER_TO_FETCH_PASSWORD': 'test'}


class MockRequest:
    def __init__(self, json_response):
        self.json_response = json_response
        self.status_code = 200

    def json(self):
        return self.json_response


def mock_request_none_attribution_charge(*args, **kwargs):
    return MockRequest({})


def mock_request_single_attribution_charge(*args, **kwargs):
    json_response = {"tutorAllocations": {
        "allocationChargeLecturing": str(LEARNING_UNIT_LECTURING_DURATION),
        "allocationChargePractical": str(LEARNING_UNIT_PRACTICAL_EXERCISES_DURATION),
        "learningUnitCharge": str(LEARNING_UNIT_CHARGE),
        "function": "COORDINATOR",
        "globalId": "00233751",
        "allocationId": ATTRIBUTION_ID,
        "year": "2017"
    }}
    return MockRequest(json_response)


def mock_request_multiple_attributions_charge(*args, **kwargs):
    json_response = {"tutorAllocations": [{
        "allocationChargeLecturing": str(LEARNING_UNIT_LECTURING_DURATION),
        "allocationChargePractical": str(LEARNING_UNIT_PRACTICAL_EXERCISES_DURATION),
        "learningUnitCharge": str(LEARNING_UNIT_CHARGE),
        "function": "COORDINATOR",
        "globalId": "00233751",
        "allocationId": ATTRIBUTION_ID,
        "year": "2017"
    },
        {
            "allocationChargeLecturing": str(0),
            "allocationChargePractical": str(0),
            "learningUnitCharge": str(LEARNING_UNIT_CHARGE),
            "function": "CO_HOLDER",
            "globalId": "00233751",
            "allocationId": OTHER_ATTRIBUTION_ID,
            "year": "2017"
        },
    ]}
    return MockRequest(json_response)


def mock_request_multiple_attributions_charge_with_missing_values(*args, **kwargs):
    json_response = {"tutorAllocations": [{
        "allocationChargeLecturing": str(LEARNING_UNIT_LECTURING_DURATION),
        "learningUnitCharge": str(LEARNING_UNIT_CHARGE),
        "function": "COORDINATOR",
        "globalId": "00233751",
        "allocationId": ATTRIBUTION_ID,
        "year": "2017"
    },
        {
            "allocationChargePractical": str(LEARNING_UNIT_PRACTICAL_EXERCISES_DURATION),
            "function": "CO_HOLDER",
            "globalId": "00233751",
            "allocationId": OTHER_ATTRIBUTION_ID,
            "year": "2017"
        },
    ]}
    return MockRequest(json_response)


class TutorChargeTest(TestCase):

    def setUp(self):
        self.create_tutor()
        self.data = []
        self.data.append(self.create_lu_yr_annual_data(CURRENT_YEAR))
        self.data.append(self.create_lu_yr_annual_data(NEXT_YEAR))
        Group.objects.get_or_create(name='students')

    def create_lu_yr_annual_data(self, a_year):
        an_academic_yr = test_academic_year.create_academic_year_with_year(a_year)
        an_academic_yr.year = a_year
        a_container_year = LearningContainerYearFactory(in_charge=True)
        a_learning_unit_year = test_learning_unit_year.create_learning_unit_year({
            'acronym': ACRONYM,
            'specific_title': TITLE,
            'academic_year': an_academic_yr,
            'weight': WEIGHT,
            'subtype': learning_unit_year_subtypes.FULL,
        })
        a_learning_unit_year.learning_container_year = a_container_year
        a_learning_unit_year.save()
        an_attribution = AttributionFactory(function=function.CO_HOLDER,
                                            learning_unit_year=a_learning_unit_year,
                                            tutor=self.a_tutor,
                                            external_id=ATTRIBUTION_EXTERNAL_ID)

        return {'academic_year':                   an_academic_yr,
                'learning_unit_year':               a_learning_unit_year,
                'attribution':                      an_attribution}

    def create_tutor(self):
        self.a_user = self.create_user(username='jacob', email='jacob@localhost', password='top_secret')
        self.a_person = test_person.create_person_with_user(self.a_user)
        Group.objects.get_or_create(name='tutors')
        self.a_tutor = test_tutor.create_tutor_with_person(self.a_person)

    def create_user(self, username, email, password):
        return User.objects.create_user(username, email, password)

    def test_get_person_from_user(self):
        self.assertEqual(tutor_charge.get_person(self.a_user), self.a_person)

    def test_get_non_existing_person_from_user(self):
        a_user_not_known = self.create_user('jacobette', 'jacobette@localhost', 'top_secret')
        self.assertIsNone(tutor_charge.get_person(a_user_not_known))

    def get_data(self, key):
        data_year = self.data[0]
        return data_year.get(key, None)

    def test_calculate_percentage_allocation_charge(self):
        self.assertEqual(tutor_charge.calculate_attribution_format_percentage_allocation_charge(
            LEARNING_UNIT_LECTURING_DURATION, LEARNING_UNIT_PRACTICAL_EXERCISES_DURATION, LEARNING_UNIT_CHARGE), "75.0")

    def test_calculate_percentage_allocation_charge_with_no_duration(self):
        self.assertIsNone(tutor_charge.calculate_attribution_format_percentage_allocation_charge(
            LEARNING_UNIT_LECTURING_DURATION, LEARNING_UNIT_PRACTICAL_EXERCISES_DURATION, 0))

    def test_format_students_email(self):
        email_expected = "{0}{1}{2}".format(tutor_charge.MAIL_TO, ACRONYM.lower(), tutor_charge.STUDENT_LIST_EMAIL_END)
        self.assertEqual(tutor_charge.get_email_students(ACRONYM, tutor_charge.YEAR_NEW_MANAGEMENT_OF_EMAIL_LIST - 1),
                         email_expected)

    def test_format_students_email_new_management(self):
        email_expected = "{0}{1}-{2}{3}".format(tutor_charge.MAIL_TO, ACRONYM.lower(),
                                                tutor_charge.YEAR_NEW_MANAGEMENT_OF_EMAIL_LIST,
                                                tutor_charge.STUDENT_LIST_EMAIL_END)
        self.assertEqual(tutor_charge.get_email_students(ACRONYM, tutor_charge.YEAR_NEW_MANAGEMENT_OF_EMAIL_LIST),
                         email_expected)

    def test_format_students_email_without_acronym(self):
        self.assertIsNone(tutor_charge.get_email_students(None, 2017))

    def test_get_schedule_url(self):
        url_expected = settings.ATTRIBUTION_CONFIG.get('TIME_TABLE_URL'). \
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
        a_learning_unit_yr = self.get_data('learning_unit_year')
        url_learning_unit = settings.ATTRIBUTION_CONFIG.get('CATALOG_URL').format(a_learning_unit_yr.academic_year.year,
                                                                                  ACRONYM.lower())
        self.assertEqual(tutor_charge.get_url_learning_unit_year(a_learning_unit_yr), url_learning_unit)

    def test_find_january_note(self):
        student_performance = test_student_performance.create_student_performance()
        an_academic_yr = test_academic_year.create_academic_year_with_year(student_performance.academic_year)
        a_learning_unit_year = test_learning_unit_year.create_learning_unit_year({
            'acronym': 'LINGI2145',
            'specific_title': TITLE,
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

    @mock.patch('requests.get', side_effect=mock_request_multiple_attributions_charge)
    def test_list_teaching_charge_for_multiple_attributions_less_in_json(self, mock_requests_get):

        an_other_attribution = AttributionFactory(learning_unit_year=self.get_data('learning_unit_year'),
                                                  tutor=self.a_tutor,
                                                  external_id=OTHER_ATTRIBUTION_EXTERNAL_ID)
        inexisting_external_id = "osis.attribution_8082"

        attribution_not_in_json = AttributionFactory(learning_unit_year=self.get_data('learning_unit_year'),
                                                     tutor=self.a_tutor,
                                                     external_id=inexisting_external_id)

        teaching_charge = tutor_charge.list_teaching_charge(self.a_tutor.person, self.get_data('academic_year'))

        self.assertTrue(mock_requests_get.called)

        attributions = teaching_charge["attributions"]
        tot_lecturing = teaching_charge["tot_lecturing"]
        tot_practical = teaching_charge["tot_practical"]

        self.assertEqual(len(attributions), 3)
        self.assertEqual(tot_lecturing, LEARNING_UNIT_LECTURING_DURATION)
        self.assertEqual(tot_practical, LEARNING_UNIT_PRACTICAL_EXERCISES_DURATION)


    def test_get_learning_unit_enrollments_list(self):
        luy_full = self.data[0]['learning_unit_year']
        luy_partim = test_learning_unit_year.create_learning_unit_year({
            'acronym': "{}A".format(ACRONYM),
            'specific_title': TITLE,
            'academic_year': self.data[0]['academic_year'],
            'weight': WEIGHT,
            'subtype': learning_unit_year_subtypes.PARTIM,
        })
        luy_partim.learning_container_year = luy_full.learning_container_year
        luy_partim.save()
        for i in range(5):
            LearningUnitEnrollmentFactory(learning_unit_year=luy_full)
            LearningUnitEnrollmentFactory(learning_unit_year=luy_partim)
        # The students of the partim don't have to be in the result list
        self.assertEqual(len(tutor_charge._get_learning_unit_yr_enrollments_list(luy_full)), 5)

ACCESS_DENIED = 401


class HomeTest(TestCase):
    def setUp(self):
        Group.objects.get_or_create(name='tutors')
        self.person = PersonFactory()
        self.tutor = TutorFactory(person=self.person)

        attribution_permission = Permission.objects.get(codename='can_access_attribution')
        self.person.user.user_permissions.add(attribution_permission)

        today = datetime.datetime.today()
        self.academic_year = AcademicYearFactory(year=today.year, start_date=today-datetime.timedelta(days=5),
                                                 end_date=today+datetime.timedelta(days=5))
        self.learning_unit_year = LearningUnitYearFactory(academic_year=self.academic_year,
                                                          learning_container_year__academic_year=self.academic_year,
                                                          learning_container_year__in_charge=True)
        self.attribution = AttributionFactory(function=function.CO_HOLDER,
                                              learning_unit_year=self.learning_unit_year,
                                              tutor=self.tutor,
                                              external_id=ATTRIBUTION_EXTERNAL_ID)

        self.url = reverse('attribution_home')
        self.client.force_login(self.person.user)

    def test_user_not_logged(self):
        self.client.logout()
        response = self.client.get(self.url)

        self.assertRedirects(response, "/login/?next={}".format(self.url))

    def test_user_without_permission(self):
        a_person = PersonFactory()
        self.client.force_login(a_person.user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, ACCESS_DENIED)
        self.assertTemplateUsed(response, "access_denied.html")

    def test_person_without_global_id(self):
        self.person.global_id = None
        self.person.save()

        response = self.client.get(self.url)

        self.assertTemplateUsed(response, 'tutor_charge.html')

        self.assertEqual(response.context['user'], self.person.user)
        self.assertEqual(len(response.context['attributions']), 1)
        self.assertEqual(response.context['year'], int(self.academic_year.year))
        self.assertEqual(response.context['tot_lecturing'], 0)
        self.assertEqual(response.context['tot_practical'], 0)
        self.assertEqual(response.context['academic_year'], self.academic_year)
        self.assertEqual(response.context['global_id'], None)
        self.assertEqual(response.context['error'], True)

        self.assertIsInstance(response.context['formset'], BaseFormSet)

    def test_user_without_person(self):
        self.person.delete()

        response = self.client.get(self.url)

        self.assertTemplateUsed(response, 'tutor_charge.html')

        self.assertEqual(response.context['user'], None)
        self.assertEqual(response.context['attributions'], None)
        self.assertEqual(response.context['year'], int(self.academic_year.year))
        self.assertEqual(response.context['tot_lecturing'], None)
        self.assertEqual(response.context['tot_practical'], None)
        self.assertEqual(response.context['academic_year'], self.academic_year)
        self.assertEqual(response.context['global_id'], None)
        self.assertEqual(response.context['error'], False)

        self.assertIsInstance(response.context['formset'], BaseFormSet)

    def test_user_without_tutor(self):
        self.tutor.delete()

        response = self.client.get(self.url)

        self.assertTemplateUsed(response, 'tutor_charge.html')

        self.assertEqual(response.context['user'], self.person.user)
        self.assertEqual(response.context['attributions'], None)
        self.assertEqual(response.context['year'], int(self.academic_year.year))
        self.assertEqual(response.context['tot_lecturing'], None)
        self.assertEqual(response.context['tot_practical'], None)
        self.assertEqual(response.context['academic_year'], self.academic_year)
        self.assertEqual(response.context['global_id'], None)
        self.assertEqual(response.context['error'], False)

        self.assertIsInstance(response.context['formset'], BaseFormSet)

    def test_without_current_academic_year(self):
        self.academic_year.year -= 1
        self.academic_year.end_date = datetime.datetime.today() - datetime.timedelta(days=3)
        self.academic_year.save()

        response = self.client.get(self.url)

        self.assertTemplateUsed(response, 'tutor_charge.html')

        self.assertEqual(response.context['user'], self.person.user)
        self.assertEqual(len(response.context['attributions']), 1)
        self.assertEqual(response.context['year'], int(datetime.datetime.now().year))
        self.assertEqual(response.context['tot_lecturing'], 0)
        self.assertEqual(response.context['tot_practical'], 0)
        self.assertEqual(response.context['academic_year'], None)
        self.assertEqual(response.context['global_id'], None)
        self.assertEqual(response.context['error'], True)

        self.assertIsInstance(response.context['formset'], BaseFormSet)

    @mock.patch('requests.get', side_effect=mock_request_none_attribution_charge)
    def test_without_attributions(self, mock_requests_get):
        self.attribution.delete()
        response = self.client.get(self.url, mock_requests_get)

        self.assertTrue(mock_requests_get.called)

        self.assertTemplateUsed(response, 'tutor_charge.html')

        self.assertEqual(response.context['user'], self.person.user)
        self.assertEqual(response.context['attributions'], None)
        self.assertEqual(response.context['year'], int(self.academic_year.year))
        self.assertEqual(response.context['tot_lecturing'], 0)
        self.assertEqual(response.context['tot_practical'], 0)
        self.assertEqual(response.context['academic_year'], self.academic_year)
        self.assertEqual(response.context['global_id'], self.person.global_id)
        self.assertEqual(response.context['error'], False)

        self.assertIsInstance(response.context['formset'], BaseFormSet)

    @override_settings(ATTRIBUTION_CONFIG={})
    def test_when_not_configuration_for_attribution(self):
        del settings.ATTRIBUTION_CONFIG

        response = self.client.get(self.url)

        self.assertTemplateUsed(response, 'tutor_charge.html')

        self.assertEqual(response.context['user'], self.person.user)
        self.assertEqual(len(response.context['attributions']), 1)
        self.assertEqual(response.context['year'], int(self.academic_year.year))
        self.assertEqual(response.context['tot_lecturing'], 0)
        self.assertEqual(response.context['tot_practical'], 0)
        self.assertEqual(response.context['academic_year'], self.academic_year)
        self.assertEqual(response.context['global_id'], self.person.global_id)
        self.assertEqual(response.context['error'], True)

        self.assertIsInstance(response.context['formset'], BaseFormSet)

    @mock.patch('requests.get', side_effect=RequestException)
    def test_when_exception_occured_during_request_of_webservice(self, mock_requests_get):
        response = self.client.get(self.url)

        self.assertTrue(mock_requests_get.called)

        self.assertTemplateUsed(response, 'tutor_charge.html')

        self.assertEqual(response.context['user'], self.person.user)
        self.assertEqual(len(response.context['attributions']), 1)
        self.assertEqual(response.context['year'], int(self.academic_year.year))
        self.assertEqual(response.context['tot_lecturing'], 0)
        self.assertEqual(response.context['tot_practical'], 0)
        self.assertEqual(response.context['academic_year'], self.academic_year)
        self.assertEqual(response.context['global_id'], self.person.global_id)
        self.assertEqual(response.context['error'], True)

        self.assertIsInstance(response.context['formset'], BaseFormSet)

    @override_settings(ATTRIBUTION_CONFIG=get_attribution_config_settings())
    @mock.patch('requests.get', side_effect=mock_request_single_attribution_charge)
    def test_for_one_attribution(self, mock_requests_get):

        response = self.client.get(self.url)

        self.assertTrue(mock_requests_get.called)

        self.assertTemplateUsed(response, 'tutor_charge.html')

        self.assertEqual(response.context['user'], self.person.user)
        self.assertEqual(response.context['year'], int(self.academic_year.year))
        self.assertEqual(response.context['tot_lecturing'], LEARNING_UNIT_LECTURING_DURATION)
        self.assertEqual(response.context['tot_practical'], LEARNING_UNIT_PRACTICAL_EXERCISES_DURATION)
        self.assertEqual(response.context['academic_year'], self.academic_year)
        self.assertEqual(response.context['global_id'], self.person.global_id)
        self.assertEqual(response.context['error'], False)

        self.assertIsInstance(response.context['formset'], BaseFormSet)

        self.assertEqual(len(response.context['attributions']), 1)
        attribution = response.context['attributions'][0]
        self.assertEqual(attribution['acronym'], self.learning_unit_year.acronym)
        self.assertEqual(attribution['title'], self.learning_unit_year.complete_title)
        self.assertEqual(attribution['start_year'], self.attribution.start_year)
        self.assertEqual(attribution['lecturing_allocation_charge'], str(LEARNING_UNIT_LECTURING_DURATION))
        self.assertEqual(attribution['practice_allocation_charge'], str(LEARNING_UNIT_PRACTICAL_EXERCISES_DURATION))
        self.assertEqual(attribution['percentage_allocation_charge'], '75.0')
        self.assertEqual(attribution['weight'], self.learning_unit_year.credits)
        self.assertEqual(attribution['url_schedule'], "")
        self.assertEqual(attribution['url_students_list_email'], 'mailto:{}-{}@listes-student.uclouvain.be'.format(
            self.learning_unit_year.acronym.lower(),
            self.academic_year.year))
        self.assertEqual(attribution['function'], self.attribution.function)
        self.assertEqual(attribution['year'], self.academic_year.year)
        self.assertEqual(attribution['learning_unit_year_url'], "")
        self.assertEqual(attribution['learning_unit_year'], self.learning_unit_year)
        self.assertEqual(attribution['tutor_id'], self.tutor.id)

    @mock.patch('requests.get', side_effect=mock_request_multiple_attributions_charge)
    def test_for_multiple_attributions(self, mock_requests_get):
        an_other_attribution = AttributionFactory(function=function.CO_HOLDER,
                                                  learning_unit_year=self.learning_unit_year,
                                                  tutor=self.tutor,
                                                  external_id=OTHER_ATTRIBUTION_EXTERNAL_ID)

        response = self.client.get(self.url)

        self.assertTrue(mock_requests_get.called)

        self.assertTemplateUsed(response, 'tutor_charge.html')

        self.assertEqual(response.context['user'], self.person.user)
        self.assertEqual(response.context['year'], int(self.academic_year.year))
        self.assertEqual(response.context['tot_lecturing'], LEARNING_UNIT_LECTURING_DURATION)
        self.assertEqual(response.context['tot_practical'], LEARNING_UNIT_PRACTICAL_EXERCISES_DURATION)
        self.assertEqual(response.context['academic_year'], self.academic_year)
        self.assertEqual(response.context['global_id'], self.person.global_id)
        self.assertEqual(response.context['error'], False)

        self.assertIsInstance(response.context['formset'], BaseFormSet)

        self.assertEqual(len(response.context['attributions']), 2)

    @mock.patch('requests.get', side_effect=mock_request_multiple_attributions_charge)
    def test_with_attribution_not_recognized(self, mock_requests_get):
        an_other_attribution = AttributionFactory(learning_unit_year=self.learning_unit_year,
                                                  tutor=self.tutor,
                                                  external_id=OTHER_ATTRIBUTION_EXTERNAL_ID)

        inexisting_external_id = "osis.attribution_8082"
        attribution_not_in_json = AttributionFactory(learning_unit_year=self.learning_unit_year,
                                                     tutor=self.tutor,
                                                     external_id=inexisting_external_id)

        response = self.client.get(self.url)

        self.assertTrue(mock_requests_get.called)

        self.assertTemplateUsed(response, 'tutor_charge.html')

        self.assertEqual(response.context['user'], self.person.user)
        self.assertEqual(response.context['year'], int(self.academic_year.year))
        self.assertEqual(response.context['tot_lecturing'], LEARNING_UNIT_LECTURING_DURATION)
        self.assertEqual(response.context['tot_practical'], LEARNING_UNIT_PRACTICAL_EXERCISES_DURATION)
        self.assertEqual(response.context['academic_year'], self.academic_year)
        self.assertEqual(response.context['global_id'], self.person.global_id)
        self.assertEqual(response.context['error'], False)

        self.assertIsInstance(response.context['formset'], BaseFormSet)

        self.assertEqual(len(response.context['attributions']), 3)

    @mock.patch('requests.get', side_effect=mock_request_multiple_attributions_charge_with_missing_values)
    def test_with_missing_values(self, mock_requests_get):
        an_other_attribution = AttributionFactory(learning_unit_year=self.learning_unit_year,
                                                  tutor=self.tutor,
                                                  external_id=OTHER_ATTRIBUTION_EXTERNAL_ID)

        response = self.client.get(self.url)

        self.assertTrue(mock_requests_get.called)

        self.assertTemplateUsed(response, 'tutor_charge.html')

        self.assertEqual(response.context['user'], self.person.user)
        self.assertEqual(response.context['year'], int(self.academic_year.year))
        self.assertEqual(response.context['tot_lecturing'], LEARNING_UNIT_LECTURING_DURATION)
        self.assertEqual(response.context['tot_practical'], LEARNING_UNIT_PRACTICAL_EXERCISES_DURATION)
        self.assertEqual(response.context['academic_year'], self.academic_year)
        self.assertEqual(response.context['global_id'], self.person.global_id)
        self.assertEqual(response.context['error'], False)

        self.assertIsInstance(response.context['formset'], BaseFormSet)

        attributions = response.context['attributions']
        reduced_list_attributions = map(lambda attribution: [attribution["lecturing_allocation_charge"],
                                        attribution['practice_allocation_charge'],
                                        attribution['percentage_allocation_charge']], attributions)
        self.assertIn([str(LEARNING_UNIT_LECTURING_DURATION), None, "25.0"], reduced_list_attributions)

