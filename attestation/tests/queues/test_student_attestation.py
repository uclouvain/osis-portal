##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
from mock import patch

from django.conf import settings
from django.test import SimpleTestCase, override_settings

from attestation.queues.student_attestation import fetch_student_attestation
from attestation.models.enums.attestation_type import REGULAR_REGISTRATION

GLOBAL_ID = "45451200"
ACADEMIC_YEAR = 2016
ATTESTATION_TYPE = REGULAR_REGISTRATION


class FetchStudentAttestationTest(SimpleTestCase):
    @override_settings()
    def test_when_attestation_config_not_present(self):
        del settings.ATTESTATION_CONFIG
        response = fetch_student_attestation(GLOBAL_ID, ACADEMIC_YEAR, ATTESTATION_TYPE)

        self.assertEqual(response, None)

    @override_settings(ATTESTATION_CONFIG={'SERVER_TO_FETCH_URL': '', 'ATTESTATION_PATH': ''})
    def test_when_attestation_config_items_are_none(self):
        response = fetch_student_attestation(GLOBAL_ID, ACADEMIC_YEAR, ATTESTATION_TYPE)

        self.assertEqual(response, None)




