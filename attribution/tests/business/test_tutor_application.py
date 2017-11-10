##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2017 Université catholique de Louvain (http://www.uclouvain.be)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
from time import sleep

from django.contrib.auth.models import Group
from django.test import TestCase

from attribution.business import tutor_application
from attribution.tests.factories.attribution import AttributionNewFactory
from attribution.utils import tutor_application_epc
from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.learning_container_year import LearningContainerYearFactory
from base.tests.factories.person import PersonFactory
from base.tests.factories.tutor import TutorFactory


class TutorApplicationTest(TestCase):
    def setUp(self):
        # Create academic year
        self.academic_year = AcademicYearFactory(year=2017)
        # Create several learning container year - 2017
        self.lbir1200_2017 = LearningContainerYearFactory(academic_year=self.academic_year, acronym="LBIR1200")
        self.lbir1250_2017 = LearningContainerYearFactory(academic_year=self.academic_year, acronym="LBIR1250")
        self.lbir1300_2017 = LearningContainerYearFactory(academic_year=self.academic_year, acronym="LBIR1300")
        self.lagro1200_2017 = LearningContainerYearFactory(academic_year=self.academic_year, acronym="LAGRO1200")

        # Create several learning container year - 2016
        self.academic_year_2016 = AcademicYearFactory(year=2016)
        self.lbir1200_2016 = LearningContainerYearFactory(academic_year=self.academic_year_2016, acronym="LBIR1200")
        self.lbir1250_2016 = LearningContainerYearFactory(academic_year=self.academic_year_2016, acronym="LBIR1250")

        # Creation Person/Tutor
        Group.objects.create(name="tutors")
        person = PersonFactory(global_id="98363454")
        self.tutor = TutorFactory(person=person)

        applications = [
            _get_application_example(self.lbir1200_2017, '3.5', '35.6'),  # Application 2017
            _get_application_example(self.lbir1300_2017, '7.5', '25'),   # Application 2017
            _get_application_example(self.lbir1200_2016, '2', '30'),  # Application 2016
        ]
        self.attribution = AttributionNewFactory(global_id=person.global_id,
                                                 attributions=_get_attributions_default(),
                                                 applications=applications)

    def test_get_application_list(self):
        global_id = self.tutor.person.global_id
        application_list = tutor_application.get_application_list(global_id, self.academic_year)
        self.assertIsInstance(application_list, list)
        self.assertEqual(len(application_list), 2)

        application_list_in_2016 = tutor_application.get_application_list(global_id, self.academic_year_2016)
        self.assertIsInstance(application_list_in_2016, list)
        self.assertEqual(len(application_list_in_2016), 1)

    def test_get_application_list_order_by(self):
        self.attribution.applications = [
            _get_application_example(self.lbir1200_2017, '3.5', '35.6'),  # Application 2017
            _get_application_example(self.lbir1250_2017, '5', '7', tutor_application_epc.UPDATE_OPERATION),
            _get_application_example(self.lbir1300_2017, '7.5', '25')  # Application 2017
        ]
        self.attribution.save()
        global_id = self.tutor.person.global_id
        application_list = tutor_application.get_application_list(global_id, self.academic_year)
        self.assertIsInstance(application_list, list)
        self.assertEqual(len(application_list), 3)
        # Check order
        self.assertEqual(application_list[0]['acronym'], self.lbir1200_2017.acronym)
        self.assertEqual(application_list[1]['acronym'], self.lbir1300_2017.acronym)
        self.assertEqual(application_list[2]['acronym'], self.lbir1250_2017.acronym)

    def test_get_application(self):
        global_id = self.tutor.person.global_id
        application_searched = tutor_application.get_application(global_id, self.lbir1200_2017)
        self.assertTrue(application_searched)
        self.assertIsInstance(application_searched, dict)
        self.assertEqual(application_searched['acronym'], self.lbir1200_2017.acronym)

    def test_get_application_not_found(self):
        global_id = self.tutor.person.global_id
        application_searched = tutor_application.get_application(global_id, self.lagro1200_2017)
        self.assertFalse(application_searched)

    def test_create_or_update_application_creation_on_existing_user(self):
        application_to_create = _get_application_example(self.lbir1250_2017, '30', '20')
        global_id = self.tutor.person.global_id
        tutor_application.create_or_update_application(global_id, application_to_create)
        application_list = tutor_application.get_application_list(global_id, self.academic_year)
        self.assertEqual(len(application_list), 3) # We should have 3 applications now
        # We should found the newest created
        self.assertTrue(next(app for app in application_list if
                             app.get('acronym') == self.lbir1250_2017.acronym))

    def test_create_or_update_application_creation_on_new_user(self):
        # Create new tutor
        new_tutor = TutorFactory(person=PersonFactory(global_id="59898988"))
        # Submit tutor application
        application_to_create = _get_application_example(self.lbir1250_2017, '30', '20')
        global_id = new_tutor.person.global_id
        tutor_application.create_or_update_application(global_id, application_to_create)
        application_list = tutor_application.get_application_list(global_id, self.academic_year)
        self.assertEqual(len(application_list), 1)  # We should have 1 application

    def test_create_or_update_application_update(self):
        application_to_update = _get_application_example(self.lbir1200_2017, '0', '10')
        global_id = self.tutor.person.global_id
        tutor_application.create_or_update_application(global_id, application_to_update)
        application_list = tutor_application.get_application_list(global_id, self.academic_year)
        self.assertEqual(len(application_list), 2)  # We should have 2 applications
        application_updated = next(app for app in application_list if
                             app.get('acronym') == self.lbir1200_2017.acronym)
        self.assertTrue(application_updated)
        self.assertEqual(application_updated.get('acronym'), self.lbir1200_2017.acronym)
        self.assertEqual(application_updated.get('charge_lecturing_asked'), '0')
        self.assertEqual(application_updated.get('charge_practical_asked'), '10')

    def test_pending_flag(self):
        global_id = self.tutor.person.global_id
        application_searched = tutor_application.get_application(global_id, self.lbir1200_2017)
        self.assertTrue(application_searched)
        tutor_application.set_pending_flag(global_id, application_searched, tutor_application_epc.UPDATE_OPERATION)
        # Research in order to verify that have pending state
        application_searched = tutor_application.get_application(global_id, self.lbir1200_2017)
        self.assertEqual(application_searched['pending'], tutor_application_epc.UPDATE_OPERATION)
        self.assertTrue(application_searched['updated_at'])

    def test_validate_application(self):
        global_id = self.tutor.person.global_id
        application_to_create = _get_application_example(self.lbir1250_2017, '30', '20')
        application_to_create['pending'] = tutor_application_epc.UPDATE_OPERATION
        tutor_application.create_or_update_application(global_id, application_to_create)
        # Check pending state
        application_searched_not_validated = tutor_application.get_application(global_id, self.lbir1250_2017)
        self.assertEqual(application_searched_not_validated['pending'], tutor_application_epc.UPDATE_OPERATION)
        self.assertTrue(application_searched_not_validated['updated_at'])
        sleep(1) # Wait 1 sec for testing updated_at field
        # Validate
        tutor_application.validate_application(global_id, self.lbir1250_2017.acronym,
                                               self.lbir1250_2017.academic_year.year)
        application_searched_validated = tutor_application.get_application(global_id, self.lbir1250_2017)
        self.assertRaises(KeyError, lambda: application_searched_validated['pending'])
        self.assertTrue(application_searched_validated['updated_at'])
        self.assertTrue(application_searched_validated['updated_at'] >
                        application_searched_not_validated['updated_at'])

    def test_delete_application(self):
        global_id = self.tutor.person.global_id
        # Before delete
        application_searched = tutor_application.get_application(global_id, self.lbir1200_2017)
        self.assertTrue(application_searched)
        # Delete process
        acronym_to_delete = self.lbir1200_2017.acronym
        year_to_delete = self.lbir1200_2017.academic_year.year
        tutor_application.delete_application(global_id, acronym_to_delete, year_to_delete)
        # After delete
        application_searched = tutor_application.get_application(global_id, self.lbir1200_2017)
        self.assertFalse(application_searched)


def _get_attributions_default():
    return [
        {'year': 2016, 'acronym': 'LBIR1200', 'title': 'Chimie complexe', 'weight': '5.00', 'LECTURING': '22.5',
         'PRACTICAL_EXERCISES': '5.0', 'function': 'HOLDER'},
        {'year': 2017, 'acronym': 'LBIR1200', 'title': 'Chimie complexe', 'weight': '5.00', 'LECTURING': '20.5',
         'PRACTICAL_EXERCISES': '7.0', 'function': 'CO-HOLDER'},
        {'year': 2017, 'acronym': 'LBIR1300', 'title': 'Chimie complexe volume 2', 'weight': '7.50',
         'LECTURING': '12.5', 'PRACTICAL_EXERCISES': '9.5', 'function': 'HOLDER'},
    ]


def _get_application_example(learning_container_year, volume_lecturing, volume_practical_exercice, flag=None):
    return {
        'remark': 'This is the remarks',
        'course_summary': 'This is the course summary',
        'charge_lecturing_asked': volume_lecturing,
        'charge_practical_asked': volume_practical_exercice,
        'acronym': learning_container_year.acronym,
        'year': learning_container_year.academic_year.year,
        'pending': flag
    }