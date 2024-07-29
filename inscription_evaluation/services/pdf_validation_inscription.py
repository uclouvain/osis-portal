##############################################################################
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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
from functools import partial
import osis_inscription_evaluation_sdk
from base.models.person import Person
from base.services.utils import call_api
from osis_inscription_evaluation_sdk.api import validation_inscription_api
from frontoffice.settings.osis_sdk import inscription_evaluation as inscription_evaluation_sdk


class PdfValidationInscriptionService:
    @staticmethod
    def recuperer(person: 'Person', uuid_fichier):
        return _pdf_validation_inscription_api_call(person, "ma_validation_inscription", uuid=uuid_fichier)


_pdf_validation_inscription_api_call = partial(
    call_api,
    inscription_evaluation_sdk,
    osis_inscription_evaluation_sdk,
    validation_inscription_api.ValidationInscriptionApi,
)
