##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2018 Université catholique de Louvain (http://www.uclouvain.be)
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
from unittest.mock import patch

from django.test import TestCase

from base.tests.factories.student import StudentFactory
from dashboard.business.id_data import get_student_id_data


class TestStudentData(TestCase):

    @patch('dashboard.business.id_data.__fetch_student_id_data')
    def test_get_student_data(self, mock_client_call):
        with open("dashboard/tests/resources/student_id_data.json") as json_file:
            data_as_json = json_file.read()
        mock_client_call.return_value = json.loads(data_as_json)
        student = StudentFactory()
        expected_data = {
            'main_data': {
                'anneeAcademique': 2020,
                'bourseAutre': 'CIUF',
                'codeEtatInscription': 1,
                'codeStatut': 60,
                'dateNaissance': '08/08/1912',
                'etatInscription': 'Inscrit au rôle',
                'matricFGS': '0202020',
                'nom': 'Monsiuer M',
                'noma': 16542394,
                'prenom': 'Rudolphe',
                'statut': 'Formation continue'
            },
            'private_data': {
                'matric_fgs': '0202020',
                'email': 'monemail@osis.be',
                'gsm': '+32466202020',
                'domicile': {
                    'street': 'Rue Machin, 42',
                    'street2': None,
                    'street3': None,
                    'postCode': 7965,
                    'town': 'Outsy',
                    'country': 'Belgique'
                },
                'residence': {
                    'street': 'Rue du Kot, 42',
                    'street2': 'A côté du Nignt-Shop',
                    'street3': None,
                    'postCode': 1236,
                    'town': 'Las-Bas',
                    'country': 'Belgique'
                }
            },
            'birth_data': {
                'matric_fgs': '0202020',
                'birthdate': '08/08/1912',
                'birthcity': 'GRENOBLE',
                'birthcountry': 'France'
            }
        }
        given_data = get_student_id_data(user=student.person.user)
        self.assertDictEqual(given_data, expected_data)
        given_data = get_student_id_data(registration_id=student.registration_id)
        self.assertDictEqual(given_data, expected_data)
