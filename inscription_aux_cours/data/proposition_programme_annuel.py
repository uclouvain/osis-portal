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
from decimal import Decimal
from typing import List

import attr


@attr.dataclass(auto_attribs=True, frozen=True, slots=True)
class Inscription:
    code: str
    intitule: str
    credits: Decimal


@attr.dataclass(auto_attribs=True, frozen=True, slots=True)
class InscriptionsParContexte:
    intitule: str
    cours: List[Inscription]


@attr.dataclass(auto_attribs=True, frozen=True, slots=True)
class PropositionProgrammeAnnuel:
    inscriptions_par_contexte: List['InscriptionsParContexte']

    @property
    def total_credits(self) -> 'Decimal':
        return sum([
            Decimal(cours.credits)
            for contexte in self.inscriptions_par_contexte
            for cours in contexte.cours
            if cours.credits
        ])

    @property
    def a_des_inscriptions(self) -> bool:
        return any(
            [inscription for contexte in self.inscriptions_par_contexte for inscription in contexte.cours]
        )
