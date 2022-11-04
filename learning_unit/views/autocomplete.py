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
from typing import List, Dict

from dal import autocomplete
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.functional import cached_property
from osis_learning_unit_sdk.model.learning_unit import LearningUnit

from base.models.person import Person
from learning_unit.services.learning_unit import LearningUnitService


class LearningUnitYearAutocomplete(LoginRequiredMixin, autocomplete.Select2ListView):
    name = "learning_unit_year_autocomplete"

    @cached_property
    def person(self) -> 'Person':
        return self.request.user.person

    def get_list(self) -> List['LearningUnit']:
        code = self.q.upper()
        annee = int(self.forwarded.get('annee')) if self.forwarded.get('annee') else None
        if not code or not annee:
            return []

        return LearningUnitService().search_learning_units(self.person, acronym_like=code, year=annee)

    def autocomplete_results(self, results):
        return results

    def results(self, results) -> List[Dict]:
        return [
            dict(
                id=learning_unit['acronym'],
                text=self._format_text(learning_unit),
                selected_text=learning_unit['acronym'],
            )
            for learning_unit in results
        ]

    def _format_text(self, learning_unit: 'LearningUnit') -> str:
        return f"{learning_unit['acronym']} - {learning_unit['title']}"
