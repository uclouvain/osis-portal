##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2023 Université catholique de Louvain (http://www.uclouvain.be)
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
import pathlib
from unittest.mock import patch

from django.conf import settings
from django.test import TestCase

from base.tests.factories.person import PersonFactory
from base.tests.factories.student import StudentFactory
from dashboard.business import id_data as bsn_id_data


def get_json_as_dict(json_path):
    data_as_json = pathlib.Path(json_path).read_text()
    return json.loads(data_as_json)


class TestStudentData(TestCase):
    def setUp(self):
        self.person = PersonFactory()

    @patch('dashboard.business.id_data._fetch_student_id_data')
    def test_get_student_data(self, mock_client_call):
        mock_client_call.return_value = get_json_as_dict("dashboard/tests/resources/student_id_data.json")
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
                'statut': 'Formation continue',
                'gender': 'M',
                'middlenames': 'Brigitte, Chantal',
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
                    'country': 'Belgique',
                },
                'residence': {
                    'street': 'Rue du Kot, 42',
                    'street2': 'A côté du Nignt-Shop',
                    'street3': None,
                    'postCode': 1236,
                    'town': 'Las-Bas',
                    'country': 'Belgique',
                },
            },
            'birth_data': {
                'matric_fgs': '0202020',
                'birthdate': '08/08/1912',
                'birthcity': 'GRENOBLE',
                'birthcountry': 'France',
            },
            'niss': '92041830152',
        }
        given_data = bsn_id_data.get_student_id_data(registration_id=student.registration_id)
        self.assertDictEqual(given_data, expected_data)

    @patch('dashboard.business.id_data._get_niss')
    @patch('dashboard.business.id_data._get_birth_data')
    @patch('dashboard.business.id_data._get_personal_data')
    @patch('dashboard.business.id_data._get_main_data')
    def test_fetch_student_data(self, main_data_mock, private_data_mock, birth_data_mock, niss_mock):
        main_data_mock.return_value = get_json_as_dict("dashboard/tests/resources/student_main_data.json")
        private_data_mock.return_value = get_json_as_dict("dashboard/tests/resources/student_private_data.json")
        birth_data_mock.return_value = get_json_as_dict("dashboard/tests/resources/student_birth_data.json")
        niss_mock.return_value = "92041830152"
        student = StudentFactory()
        given_data = bsn_id_data._fetch_student_id_data(student)
        expected_data = {
            'registration_service_url': settings.REGISTRATION_ADMINISTRATION_URL,
            'personal_data': {
                'matric_fgs': '0202020',
                'email': 'monemail@osis.be',
                'gsm': '+32466202020',
                'domicile': {
                    'street': 'Rue Machin, 42',
                    'street2': None,
                    'street3': None,
                    'postCode': 7965,
                    'town': 'Outsy',
                    'country': 'Belgique',
                },
                'residence': {
                    'street': 'Rue du Kot, 42',
                    'street2': 'A côté du Nignt-Shop',
                    'street3': None,
                    'postCode': 1236,
                    'town': 'Las-Bas',
                    'country': 'Belgique',
                },
            },
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
                'statut': 'Formation continue',
                'gender': 'M',
                'middlenames': 'Brigitte, Chantal',
            },
            'birth_data': {
                'matric_fgs': '0202020',
                'birthdate': '08/08/1912',
                'birthcity': 'GRENOBLE',
                'birthcountry': 'France',
            },
            'niss': '92.04.18-301.52',
        }
        self.assertDictEqual(given_data, expected_data)

    @patch('dashboard.business.id_data._get_data_from_esb')
    def test_get_main_data(self, mock_esb):
        mock_esb.return_value = get_json_as_dict("dashboard/tests/resources/esb_student_main_data.json")
        student = StudentFactory()
        given_data = bsn_id_data._get_main_data(student)
        expected_data = {
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
            'statut': 'Formation continue',
            'email': student.email,
            'gender': 'M',
            'middlenames': 'Brigitte, Chantal',
        }
        self.assertDictEqual(given_data, expected_data)

    @patch('dashboard.business.id_data._get_data_from_esb')
    def test_get_personal_data(self, mock_esb):
        mock_esb.return_value = get_json_as_dict("dashboard/tests/resources/esb_student_private_data.json")
        student = StudentFactory()
        given_data = bsn_id_data._get_personal_data(student)
        expected_data = {
            'matric_fgs': '0202020',
            'email': 'monemail@osis.be',
            'gsm': '+32466202020',
            'domicile': {
                'street': 'Rue Machin, 42',
                'street2': None,
                'street3': None,
                'postCode': 7965,
                'town': 'Outsy',
                'country': 'Belgique',
            },
            'residence': {
                'street': 'Rue du Kot, 42',
                'street2': 'A côté du Nignt-Shop',
                'street3': None,
                'postCode': 1236,
                'town': 'Las-Bas',
                'country': 'Belgique',
            },
        }
        self.assertDictEqual(given_data, expected_data)

    @patch('dashboard.business.id_data._get_data_from_esb')
    def test_get_birth_data(self, mock_esb):
        mock_esb.return_value = get_json_as_dict("dashboard/tests/resources/esb_student_birth_data.json")
        student = StudentFactory()
        given_data = bsn_id_data._get_birth_data(student)
        expected_data = {
            'matric_fgs': '0202020',
            'birthdate': '08/08/1912',
            'birthcity': 'GRENOBLE',
            'birthcountry': 'France',
        }
        self.assertDictEqual(given_data, expected_data)

    @patch('dashboard.business.id_data._get_data_from_esb')
    def test_get_niss(self, mock_esb):
        mock_esb.return_value = {"return": {"niss": "92041830152"}}
        student = StudentFactory()
        given_data = bsn_id_data._get_formated_niss(student)
        expected_data = "92.04.18-301.52"
        self.assertEqual(given_data, expected_data)

    @patch('dashboard.business.id_data._get_data_from_esb')
    def test_get_data_from_esb(self, mock_esb):
        mock_esb.return_value = get_json_as_dict("dashboard/tests/resources/esb_test.json")
        given_data = bsn_id_data._get_data_from_esb("test")
        expected_data = {'return': 'TEST'}
        self.assertDictEqual(given_data, expected_data)
