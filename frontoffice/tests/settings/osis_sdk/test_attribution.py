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
import mock
import osis_attribution_sdk
from django.test import SimpleTestCase, override_settings

from base.tests.factories.person import PersonFactory
from frontoffice.settings.osis_sdk import attribution as attribution_sdk


@override_settings(
    OSIS_ATTRIBUTION_SDK_HOST="http://dummy-api.com/api/attribution",
    OSIS_PORTAL_TOKEN="generic-token",
)
class BuildConfigurationAttributionTestCase(SimpleTestCase):

    def test_build_configuration_case_anonymous_call(self):
        configuration = attribution_sdk.build_configuration()

        self.assertIsInstance(configuration, osis_attribution_sdk.Configuration)
        self.assertEqual(configuration.host, "http://dummy-api.com/api/attribution")
        self.assertDictEqual(
            configuration.api_key,
            {"Token": "generic-token"}
        )

    @mock.patch('frontoffice.settings.osis_sdk.utils.get_user_token', return_value="personal-token")
    def test_build_configuration_case_call_with_person_provided(self, mock_get_token_from_osis):
        person = PersonFactory.build()

        configuration = attribution_sdk.build_configuration(person=person)
        self.assertIsInstance(configuration, osis_attribution_sdk.Configuration)
        self.assertEqual(configuration.host, "http://dummy-api.com/api/attribution")
        self.assertDictEqual(
            configuration.api_key,
            {"Token": "personal-token"}
        )
