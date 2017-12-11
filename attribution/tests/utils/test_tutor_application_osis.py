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
from attribution.utils import tutor_application_osis
from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.learning_container_year import LearningContainerYearFactory
from base.tests.factories.person import PersonFactory
from base.tests.factories.tutor import TutorFactory


class TestTutorApplicationEpc(TestCase):
    def setUp(self):
        self.academic_year = AcademicYearFactory(year=2017)
        external_id = tutor_application_osis.LEARNING_CONTAINER_YEAR_PREFIX_EXTERNAL_ID + '35654987_2017'
        self.lbir1200 = LearningContainerYearFactory(academic_year=self.academic_year, acronym="LBIR1200",
                                                     external_id=external_id)
        self.lagro2630 = LearningContainerYearFactory(academic_year=self.academic_year, acronym="LAGRO2630")

        # Creation Person/Tutor
        Group.objects.create(name="tutors")
        person = PersonFactory(global_id="98363454")
        external_id = tutor_application_osis.TUTOR_PREFIX_EXTERNAL_ID + '2089590559'
        self.tutor = TutorFactory(external_id=external_id, person=person)

        # Create two tutor applications
        applications = [_get_application_example(self.lbir1200, '30.5', '40.5'),
                        _get_application_example(self.lagro2630, '12.5', '10.5')]
        self.attribution_new = AttributionNewFactory(
            global_id=person.global_id,
            applications=applications
        )

    def test_process_message_update_operation(self):
        person = self.tutor.person
        _set_all_application_in_pending_state(self.attribution_new.applications)
        self.attribution_new.save()
        self.assertEqual(len(self.attribution_new.applications), 2)
        self.assertEqual(self.attribution_new.applications[0]['pending'], tutor_application_osis.UPDATE_OPERATION)
        self.assertEqual(self.attribution_new.applications[1]['pending'], tutor_application_osis.UPDATE_OPERATION)

        body = [{
            'global_id': person.global_id,
            'tutor_applications': [{
                'acronym': 'LBIR1200',
                'year': self.academic_year.year,
                'charge_lecturing_asked': '0',
                'charge_practical_asked': '0',
                'last_changed': "2020-12-08 09:58:57+00:00"
            }]
        }]
        body_encoded = bytearray(json.dumps(body), "utf-8")
        tutor_application_osis.process_message(body_encoded)
        self.attribution_new.refresh_from_db()
        self.assertEqual(self.attribution_new.applications[0]['charge_lecturing_asked'], '0')

    def test_process_message_no_update_operation(self):
        person = self.tutor.person
        _set_all_application_in_pending_state(self.attribution_new.applications)
        self.attribution_new.save()
        self.assertEqual(len(self.attribution_new.applications), 2)
        self.assertEqual(self.attribution_new.applications[0]['pending'], tutor_application_osis.UPDATE_OPERATION)
        self.assertEqual(self.attribution_new.applications[1]['pending'], tutor_application_osis.UPDATE_OPERATION)

        body = [{
            'global_id': person.global_id,
            'tutor_applications': [{
                'acronym': 'LAGRO2630',
                'year': self.academic_year.year,
                'charge_lecturing_asked': '0',
                'charge_practical_asked': '0',
                'last_changed': "2016-12-08 09:58:57+00:00"
            }]
        }]
        body_encoded = bytearray(json.dumps(body), "utf-8")
        tutor_application_osis.process_message(body_encoded)
        self.attribution_new.refresh_from_db()
        self.assertEqual(self.attribution_new.applications[0]['charge_lecturing_asked'], '12.5')

    def test_process_message_with_delete_pending(self):
        person = self.tutor.person
        _set_all_application_in_pending_delete(self.attribution_new.applications)
        self.attribution_new.save()
        self.assertEqual(len(self.attribution_new.applications), 2)

        body = [{
            'global_id': person.global_id,
            'tutor_applications': [{
                'acronym': 'LAGRO2630',
                'year': self.academic_year.year,
                'charge_lecturing_asked': '0',
                'charge_practical_asked': '0',
                'last_changed': "2016-12-08 09:58:57+00:00"
            }]
        }]
        body_encoded = bytearray(json.dumps(body), "utf-8")
        tutor_application_osis.process_message(body_encoded)
        self.attribution_new.refresh_from_db()
        self.assertEqual(len(self.attribution_new.applications), 1)
        self.assertEqual(self.attribution_new.applications[0]['charge_lecturing_asked'], '12.5')


def _get_application_example(learning_container_year, volume_lecturing, volume_practical_exercice):
    return {
        'remark': 'This is the remarks',
        'course_summary': 'This is the course summary',
        'charge_lecturing_asked': volume_lecturing,
        'charge_practical_asked': volume_practical_exercice,
        'acronym': learning_container_year.acronym,
        'year': learning_container_year.academic_year.year,
        'last_changed': "2017-12-08 09:58:57+00:00"
    }


def _set_all_application_in_pending_state(applications):
    for application in applications:
        application['pending'] = tutor_application_osis.UPDATE_OPERATION


def _set_all_application_in_pending_delete(applications):
    for application in applications:
        application['pending'] = tutor_application_osis.DELETE_OPERATION