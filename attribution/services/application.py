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
from decimal import Decimal
from typing import List

import osis_attribution_sdk
from django.conf import settings
from django.http import Http404
from osis_attribution_sdk.model.application_create_command import ApplicationCreateCommand
from osis_attribution_sdk.model.application_update_command import ApplicationUpdateCommand
from osis_attribution_sdk.model.renew_attribution_about_to_expire_command import RenewAttributionAboutToExpireCommand

from base.models.person import Person
from frontoffice.settings.osis_sdk import attribution as attribution_sdk

from osis_attribution_sdk.api import application_api


logger = logging.getLogger(settings.DEFAULT_LOGGER)


class ApplicationService:
    @staticmethod
    def search_vacant_courses(code: str, allocation_faculty: str, person: Person):
        # TODO: Support pagination
        configuration = attribution_sdk.build_configuration(person)
        with osis_attribution_sdk.ApiClient(configuration) as api_client:
            api_instance = application_api.ApplicationApi(api_client)
            api_response = api_instance.vacantcourses_list(
                code=code,
                allocation_faculty=allocation_faculty
            )
            return getattr(api_response, 'results', [])

    @staticmethod
    def get_vacant_course(code: str, person: Person):
        results = ApplicationService.search_vacant_courses(code=code, allocation_faculty='', person=person)
        if len(results) == 1:
            return results[0]
        raise Http404

    @staticmethod
    def get_applications(person: Person):
        configuration = attribution_sdk.build_configuration(person)
        with osis_attribution_sdk.ApiClient(configuration) as api_client:
            api_instance = application_api.ApplicationApi(api_client)
            api_response = api_instance.application_list()
            return getattr(api_response, 'results', [])

    @staticmethod
    def get_application(application_uuid: str, person: Person):
        applications = ApplicationService.get_applications(person)
        try:
            return next(application for application in applications if applications.uuid == application_uuid)
        except StopIteration:
            raise Http404

    @staticmethod
    def get_attribution_about_to_expires(person: Person):
        configuration = attribution_sdk.build_configuration(person)
        with osis_attribution_sdk.ApiClient(configuration) as api_client:
            api_instance = application_api.ApplicationApi(api_client)
            api_response = api_instance.attributionsabouttoexpire_list()
            return getattr(api_response, 'results', [])

    @staticmethod
    def create_application(
        vacant_course_code: str,
        lecturing_volume: Decimal,
        practical_volume: Decimal,
        remark: str,
        course_summary: str,
        person: Person
    ):
        configuration = attribution_sdk.build_configuration(person)
        with osis_attribution_sdk.ApiClient(configuration) as api_client:
            api_instance = application_api.ApplicationApi(api_client)
            command = ApplicationCreateCommand(
                code=vacant_course_code,
                lecturing_volume=str(lecturing_volume),
                practical_volume=str(practical_volume),
                remark=remark,
                course_summary=course_summary,
            )
            return api_instance.application_create(application_create_command=command)

    @staticmethod
    def update_application(
        application_uuid: str,
        lecturing_volume: Decimal,
        practical_volume: Decimal,
        remark: str,
        course_summary: str,
        person: Person
    ):
        configuration = attribution_sdk.build_configuration(person)
        with osis_attribution_sdk.ApiClient(configuration) as api_client:
            api_instance = application_api.ApplicationApi(api_client)
            command = ApplicationUpdateCommand(
                lecturing_volume=str(lecturing_volume),
                practical_volume=str(practical_volume),
                remark=remark,
                course_summary=course_summary,
            )
            return api_instance.application_update(
                application_uuid=application_uuid,
                application_update_command=command,
            )

    @staticmethod
    def renew_attributions_about_to_expire(vacant_courses_code: List[str], person: Person):
        configuration = attribution_sdk.build_configuration(person)
        with osis_attribution_sdk.ApiClient(configuration) as api_client:
            api_instance = application_api.ApplicationApi(api_client)
            cmd = RenewAttributionAboutToExpireCommand(codes=vacant_courses_code)
            return api_instance.attributionsabouttoexpire_renew(
                renew_attribution_about_to_expire_command=cmd
            )

    @staticmethod
    def delete_application(application_uuid: str, person: Person):
        configuration = attribution_sdk.build_configuration(person)
        with osis_attribution_sdk.ApiClient(configuration) as api_client:
            api_instance = application_api.ApplicationApi(api_client)
            api_instance.application_delete(application_uuid=application_uuid)
