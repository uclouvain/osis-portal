# ##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2024 Université catholique de Louvain (http://www.uclouvain.be)
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
# ##############################################################################
import datetime
from typing import List

from osis_reference_sdk import ApiClient
from osis_reference_sdk.api import (
    academic_years_api,
)
from osis_reference_sdk.model.academic_year import AcademicYear

from frontoffice.settings.osis_sdk import reference as reference_sdk
from frontoffice.settings.osis_sdk.utils import build_mandatory_auth_headers


class AcademicYearAPIClient:
    def __new__(cls):
        api_config = reference_sdk.build_configuration()
        return academic_years_api.AcademicYearsApi(ApiClient(configuration=api_config))


class AcademicYearService:

    @classmethod
    def get_academic_years(cls, person) -> List[AcademicYear]:
        """Returns the academic years"""
        return AcademicYearAPIClient().get_academic_years(
            limit=100,
            **build_mandatory_auth_headers(person),
        ).results

    @classmethod
    def get_current_academic_year(cls, person, academic_years=None):
        """Returns the current academic year"""
        if not academic_years:
            academic_years = cls.get_academic_years(person)

        today_date = datetime.date.today()
        return next(
            (
                academic_year.year
                for academic_year in reversed(academic_years)
                if academic_year.start_date <= today_date <= academic_year.end_date
            ),
            None,
        )
