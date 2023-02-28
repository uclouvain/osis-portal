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

import osis_inscription_cours_sdk
from osis_inscription_cours_sdk.api import contact_api
from osis_inscription_cours_sdk.model.contact_faculte import ContactFaculte

from base.models.person import Person
from base.services.utils import call_api
from frontoffice.settings.osis_sdk import inscription_aux_cours as inscription_aux_cours_sdk


class ContactService:
    @classmethod
    def get_contact_faculte(
            cls,
            person: 'Person',
            sigle_formation: str,
            annee: int,
            pour_premiere_annee: bool
    ) -> 'ContactFaculte':
        return _contact_api_call(
            person,
            "contact_facultes_get",
            formation=sigle_formation,
            annee=annee,
            premiere_annee=pour_premiere_annee
        )


_contact_api_call = partial(
    call_api,
    inscription_aux_cours_sdk,
    osis_inscription_cours_sdk,
    contact_api.ContactApi
)

