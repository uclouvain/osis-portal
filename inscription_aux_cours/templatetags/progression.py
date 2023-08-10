##############################################################################
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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
from _decimal import Decimal
from typing import Optional

from django import template

register = template.Library()


@register.simple_tag(takes_context=False)
def progression_contextualisee(
    progression_annuelle: dict,
    code_mini_formation: str,
    partenariat_id: Optional[int] = None,
) -> dict:
    est_partenariat = bool(partenariat_id)
    return next(
        (
            progression_contextualisee_
            for progression_contextualisee_ in progression_annuelle['progressions_contextualisees']
            if (est_partenariat and partenariat_id == progression_contextualisee_['partenariat_id'])
            or (not est_partenariat and code_mini_formation == progression_contextualisee_['code_mini_formation'])
        ),
        None,
    )


@register.simple_tag(takes_context=False)
def credits_acquis_de_progression_contextualise(
    progression_cycle: dict,
    code_mini_formation: str,
    partenariat_id: Optional[int] = None,
) -> Decimal:
    est_partenariat = bool(partenariat_id)
    return next(
        (
            total_contextualise['credits_acquis_de_progression']
            for total_contextualise in progression_cycle['progressions_cycles_contextualisees']
            if (est_partenariat and partenariat_id == total_contextualise['partenariat_id'])
            or (not est_partenariat and code_mini_formation == total_contextualise['code_mini_formation'])
        ),
        None,
    )


@register.simple_tag(takes_context=False)
def credits_de_progression_potentielle_contextualise(
    progression_cycle: dict,
    code_mini_formation: str,
    partenariat_id: Optional[int] = None,
) -> Decimal:
    est_partenariat = bool(partenariat_id)
    progressions_potentielles_contextualisees = progression_cycle[
        'credits_de_progression_potentielle_contextualises'
    ]
    return next(
        (
            credit_de_progression_potentielle_contextualise['credits_de_progression_potentielle']
            for credit_de_progression_potentielle_contextualise in progressions_potentielles_contextualisees
            if (est_partenariat and partenariat_id == credit_de_progression_potentielle_contextualise['partenariat_id'])
            or (
                not est_partenariat
                and code_mini_formation == credit_de_progression_potentielle_contextualise['code_mini_formation']
            )
        ),
        None,
    )


@register.simple_tag(takes_context=False)
def credits_valorises_contextualise(
    progression_cycle: dict,
    code_mini_formation: str,
) -> int:
    return next(
        (
            credits_valorise['credits']
            for credits_valorise in progression_cycle['credits_valorises_contextualises']
            if code_mini_formation == credits_valorise['code_mini_formation']
        ),
        None,
    )
