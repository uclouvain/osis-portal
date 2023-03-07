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
from functools import partial
from typing import Optional

import osis_inscription_cours_sdk
from django.http import Http404
from osis_inscription_cours_sdk.api import activites_aide_reussite_api
from osis_inscription_cours_sdk.model.acces_activites_aide_reussite import AccesActivitesAideReussite
from osis_inscription_cours_sdk.model.activites_aide_reussite import ActivitesAideReussite
from osis_inscription_cours_sdk.model.demande_activites_aide_reussite import DemandeActivitesAideReussite

from base.models.person import Person
from base.services.utils import call_api
from frontoffice.settings.osis_sdk import inscription_aux_cours as inscription_aux_cours_sdk


class ActivitesAideReussiteService:
    @classmethod
    def get_activites_aide_reussite(
            cls,
            person: 'Person',
            code_programme: str,
    ) -> Optional['ActivitesAideReussite']:
        try:
            return _activites_api_call(
                person,
                "get_activites_aide_reussite",
                code_programme=code_programme,
            )
        except Http404:
            return None

    @classmethod
    def demander_a_completer_inscription_par_des_activites_de_aide_a_la_reussite(
            cls,
            person: 'Person',
            code_programme: str,
    ) -> None:
        return _activites_api_call(
            person,
            "post_activites_aide_reussite",
            code_programme=code_programme,
            demande_activites_aide_reussite=DemandeActivitesAideReussite(
                suivre_activites=True
            )
        )

    @classmethod
    def demander_a_ne_pas_completer_inscription_par_des_activites_de_aide_a_la_reussite(
            cls,
            person: 'Person',
            code_programme: str,
    ) -> None:
        return _activites_api_call(
            person,
            "post_activites_aide_reussite",
            code_programme=code_programme,
            demande_activites_aide_reussite=DemandeActivitesAideReussite(
                suivre_activites=False
            )
        )

    @classmethod
    def get_access(
            cls,
            person: 'Person',
            code_programme: str,
    ) -> 'AccesActivitesAideReussite':
        return _activites_api_call(
            person,
            "get_access",
            code_programme=code_programme
        )


_activites_api_call = partial(
    call_api,
    inscription_aux_cours_sdk,
    osis_inscription_cours_sdk,
    activites_aide_reussite_api.ActivitesAideReussiteApi
)
