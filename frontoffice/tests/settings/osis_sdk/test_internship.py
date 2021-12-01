##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2021 Université catholique de Louvain (http://www.uclouvain.be)
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
import osis_internship_sdk
from django.test import SimpleTestCase, override_settings

from frontoffice.settings.osis_sdk import internship as internship_sdk


@override_settings(
    OSIS_INTERNSHIP_SDK_HOST="http://dummy-api.com/api/internship",
    REST_FRAMEWORK_ESB_AUTHENTICATION_SECRET_KEY="esb-authentication-token",
)
class BuildConfigurationInternshipTestCase(SimpleTestCase):

    def test_build_configuration(self):
        configuration = internship_sdk.build_configuration()

        self.assertIsInstance(configuration, osis_internship_sdk.Configuration)
        self.assertEqual(configuration.host, "http://dummy-api.com/api/internship")
        self.assertDictEqual(
            configuration.api_key,
            {"Token": "esb-authentication-token"}
        )
