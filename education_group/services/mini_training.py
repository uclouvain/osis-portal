#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2022 Université catholique de Louvain (http://www.uclouvain.be)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
import logging
from functools import partial
from typing import List

import osis_education_group_sdk
from django.conf import settings
from osis_education_group_sdk.api import mini_trainings_api
from osis_education_group_sdk.model.mini_training import MiniTraining

from base.models.person import Person
from base.services.utils import call_api
from frontoffice.settings.osis_sdk import education_group as education_group_sdk

logger = logging.getLogger(settings.DEFAULT_LOGGER)


class MiniTrainingService:
    @staticmethod
    def search(
            person: Person,
            year: int = None,
            codes: List[str] = None
    ) -> List['MiniTraining']:
        kwargs = {}
        if year:
            kwargs['year'] = year
        if codes:
            # kwargs['codes'] = ",".join(codes)
            return [
                _call_api(person, "minitrainings_list", code=code, year=year).get('results')[0]
                for code in codes
            ]

        return _call_api(person, "minitrainings_list", **kwargs).get('results', [])


_call_api = partial(call_api, education_group_sdk, osis_education_group_sdk, mini_trainings_api.MiniTrainingsApi)
