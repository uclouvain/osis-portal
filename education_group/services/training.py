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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
from functools import partial

import osis_education_group_sdk
from osis_education_group_sdk.api import trainings_api
from osis_education_group_sdk.model.training_detailed import TrainingDetailed

from base.models.person import Person
from base.services.utils import call_api
from frontoffice.settings.osis_sdk import education_group as education_group_sdk


class TrainingService:
    @staticmethod
    def get_detail(
        person: 'Person',
        year: int,
        acronym: str,
    ) -> 'TrainingDetailed':
        return _call_api(person, 'trainings_read', year=str(year), acronym=acronym)

    @staticmethod
    def get_credits(
        person: 'Person',
        year: int,
        acronym: str,
    ) -> int:
        return _call_api(person, 'trainings_credits_read', year=year, acronym=acronym).credits


_call_api = partial(call_api, education_group_sdk, osis_education_group_sdk, trainings_api.TrainingsApi)
