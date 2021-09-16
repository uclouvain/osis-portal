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

import osis_offer_enrollment_sdk
import urllib3
from django.conf import settings
from osis_offer_enrollment_sdk.api import enrollment_api
from osis_offer_enrollment_sdk.model.enrollment_list import EnrollmentList

from base.models.person import Person
from frontoffice.settings.osis_sdk import offer_enrollment as offer_enrollment_sdk

logger = logging.getLogger(settings.DEFAULT_LOGGER)


class OfferEnrollmentService:
    @staticmethod
    def get_my_enrollments_list(person: Person, **kwargs) -> EnrollmentList:
        configuration = offer_enrollment_sdk.build_configuration(person)
        with osis_offer_enrollment_sdk.ApiClient(configuration) as api_client:
            api_instance = enrollment_api.EnrollmentApi(api_client)
            try:
                enrollments = api_instance.my_enrollments_list(**kwargs)
            except (osis_offer_enrollment_sdk.ApiException, urllib3.exceptions.HTTPError,) as e:
                # Run in degraded mode in order to prevent crash all app
                logger.error(e)
                enrollments = {'results': [], 'count': 0}
        return enrollments

    @staticmethod
    def get_my_enrollments_year_list(person: Person, year: int, **kwargs) -> EnrollmentList:
        configuration = offer_enrollment_sdk.build_configuration(person)
        with osis_offer_enrollment_sdk.ApiClient(configuration) as api_client:
            api_instance = enrollment_api.EnrollmentApi(api_client)
            try:
                enrollments = api_instance.my_enrollments_year_list(
                    year=year,
                    **kwargs
                )
            except (osis_offer_enrollment_sdk.ApiException, urllib3.exceptions.HTTPError,) as e:
                # Run in degraded mode in order to prevent crash all app
                logger.error(e)
                enrollments = {'results': [], 'count': 0}
        return enrollments
