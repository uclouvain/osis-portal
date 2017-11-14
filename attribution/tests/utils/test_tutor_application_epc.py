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
import json

from django.contrib.auth.models import Group
from django.test import TestCase

from attribution.tests.factories.attribution import AttributionNewFactory
from attribution.utils import tutor_application_epc
from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.learning_container_year import LearningContainerYearFactory
from base.tests.factories.person import PersonFactory
from base.tests.factories.tutor import TutorFactory


class TestTutorApplicationEpc(TestCase):
    def setUp(self):
        self.academic_year = AcademicYearFactory(year=2017)
        external_id = tutor_application_epc.LEARNING_CONTAINER_YEAR_PREFIX_EXTERNAL_ID + '35654987_2017'
        self.lbir1200 = LearningContainerYearFactory(academic_year=self.academic_year, acronym="LBIR1200",
                                                     external_id=external_id)
        self.lagro2630 = LearningContainerYearFactory(academic_year=self.academic_year, acronym="LAGRO2630")

        # Creation Person/Tutor
        Group.objects.create(name="tutors")
        person = PersonFactory(global_id="98363454")
        external_id = tutor_application_epc.TUTOR_PREFIX_EXTERNAL_ID + '2089590559'
        self.tutor = TutorFactory(external_id=external_id, person=person)

        # Create two tutor applications
        applications = [_get_application_example(self.lbir1200, '30.5', '40.5'),
                        _get_application_example(self.lagro2630, '12.5', '0')]
        self.attribution = AttributionNewFactory(
            global_id=person.global_id,
            applications=applications
        )

    def test_extract_learning_container_year_epc_info(self):
        learning_container_info = tutor_application_epc._extract_learning_container_year_epc_info('LBIR1200', 2017)
        self.assertIsInstance(learning_container_info, dict)
        self.assertEqual(learning_container_info['reference'], '35654987')
        self.assertEqual(learning_container_info['year'], 2017)

    def test_extract_learning_container_year_epc_info_empty(self):
        learning_container_info = tutor_application_epc._extract_learning_container_year_epc_info('LBIR1250', 2017)
        self.assertIsInstance(learning_container_info, dict)
        self.assertFalse(learning_container_info)

    def test_extract_learning_container_year_epc_info_with_external_id_empty(self):
        self.lbir1200.external_id = None
        self.lbir1200.save()
        learning_container_info = tutor_application_epc._extract_learning_container_year_epc_info('LBIR1200', 2017)
        self.assertIsInstance(learning_container_info, dict)
        self.assertFalse(learning_container_info)

    def test_extract_tutor_epc_info(self):
        person = self.tutor.person
        tutor_info = tutor_application_epc._extract_tutor_epc_info(person.global_id)
        self.assertEqual(tutor_info, '2089590559')

    def test_extract_tutor_epc_info_with_external_id_empty(self):
        person = self.tutor.person
        self.tutor.external_id = None
        self.tutor.save()
        tutor_info = tutor_application_epc._extract_tutor_epc_info(person.global_id)
        self.assertFalse(tutor_info)

    def test_extract_tutor_epc_info_with_wrong_global_id(self):
        tutor_info = tutor_application_epc._extract_tutor_epc_info('000000088')
        self.assertFalse(tutor_info)

    def test_convert_to_epc_application(self):
        person = self.tutor.person
        application = _get_application_example(self.lbir1200, '30.5', '40.5')

        epc_message = tutor_application_epc._convert_to_epc_application(
            global_id=person.global_id,
            application=application)

        self.assertTrue(epc_message)
        self.assertEqual(epc_message['remark'], application['remark'])
        self.assertEqual(epc_message['course_summary'], application['course_summary'])
        self.assertEqual(epc_message['lecturing_allocation'], application['charge_lecturing_asked'])
        self.assertEqual(epc_message['practical_allocation'], application['charge_practical_asked'])
        self.assertEqual(epc_message['tutor'], '2089590559')
        self.assertIsInstance(epc_message['learning_container_year'], dict)
        self.assertEqual(epc_message['learning_container_year']['reference'], '35654987')
        self.assertEqual(epc_message['learning_container_year']['year'], 2017)

    def test_process_message_delete_operation(self):
        person = self.tutor.person
        self.assertEqual(len(self.attribution.applications), 2)
        body = {
            'operation': tutor_application_epc.DELETE_OPERATION,
            'global_id': person.global_id,
            'acronym': 'LBIR1200',
            'year': 2017
        }
        tutor_application_epc.process_message(json.dumps(body))
        # Check if the application is removed
        self.attribution.refresh_from_db()
        self.assertEqual(len(self.attribution.applications), 1)
        attribution_left = self.attribution.applications[0]
        self.assertEqual(attribution_left['acronym'], self.lagro2630.acronym)

    def test_process_message_update_operation(self):
        person = self.tutor.person
        _set_all_application_in_pending_state(self.attribution.applications)
        self.attribution.save()
        ## Check if all are in pending
        self.assertEqual(len(self.attribution.applications), 2)
        self.assertEqual(self.attribution.applications[0]['pending'], tutor_application_epc.UPDATE_OPERATION)
        self.assertEqual(self.attribution.applications[1]['pending'], tutor_application_epc.UPDATE_OPERATION)

        body = {
            'operation': tutor_application_epc.UPDATE_OPERATION,
            'global_id': person.global_id,
            'acronym': 'LBIR1200',
            'year': 2017
        }
        tutor_application_epc.process_message(json.dumps(body))
        # Check if the application is removed
        self.attribution.refresh_from_db()
        applications_not_pending = [application for application in self.attribution.applications if
                                    not "pending" in application]
        self.assertEqual(len(applications_not_pending), 1)


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


def _set_all_application_in_pending_state(applications):
    for application in applications:
        application['pending'] = tutor_application_epc.UPDATE_OPERATION
