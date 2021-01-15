# -*- coding: utf-8 -*-
############################################################################
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
############################################################################

from django.conf import settings
from osis_internship_sdk.api.default_api import DefaultApi
from osis_internship_sdk.api_client import ApiClient
from osis_internship_sdk.configuration import Configuration


class InternshipAPIClient:

    def __new__(cls):
        api_config = Configuration()
        api_config.api_key['Authorization'] = "Token "+settings.OSIS_PORTAL_TOKEN
        api_config.host = settings.URL_INTERNSHIP_API
        return DefaultApi(api_client=ApiClient(configuration=api_config))
