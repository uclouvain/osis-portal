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
import logging

import osis_education_group_sdk
from django.conf import settings


logger = logging.getLogger(settings.DEFAULT_LOGGER)


def build_configuration() -> osis_education_group_sdk.Configuration:
    """
    Return SDK configuration of education group
    """
    if not settings.OSIS_EDUCATION_GROUP_SDK_HOST:
        logger.debug("'OSIS_EDUCATION_GROUP_SDK_HOST' setting must be set in configuration")

    if not settings.REST_FRAMEWORK_ESB_AUTHENTICATION_SECRET_KEY:
        logger.debug("'REST_FRAMEWORK_ESB_AUTHENTICATION_SECRET_KEY' setting must be set in configuration")

    return osis_education_group_sdk.Configuration(
        host=settings.OSIS_EDUCATION_GROUP_SDK_HOST,
        api_key_prefix={
            'Token': settings.OSIS_EDUCATION_GROUP_SDK_API_KEY_PREFIX
        },
        api_key={
            'Token': settings.REST_FRAMEWORK_ESB_AUTHENTICATION_SECRET_KEY
        })
