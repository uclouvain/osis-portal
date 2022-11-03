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

import requests
from django.conf import settings
from localflavor.generic.validators import IBANValidator
from requests import RequestException

logger = logging.getLogger(settings.DEFAULT_LOGGER)


class IBANValidatorService:

    @classmethod
    def validate(cls, iban: str) -> bool:
        cls._validate_localflavor(iban)
        cls._validate_esb_free(iban)
        return True

    @classmethod
    def _validate_localflavor(cls, iban: str):
        Validate = IBANValidator()
        try:
            Validate(iban)
        except Exception as e:
            raise IBANValidatorException(message=e.messages) from e

    @classmethod
    def _validate_esb_free(cls, iban: str):
        # Works only for Belgium, Germany, Netherlands, Luxembourg, Switzerland, Austria, Liechtenstein
        endpoint = settings.ESB_IBAN_ENDPOINT.format(iban=iban.replace(' ', ''))
        url = "{esb_api}/{endpoint}".format(esb_api=settings.ESB_URL, endpoint=endpoint)
        try:
            result = requests.get(
                url,
                headers={"Authorization": settings.ESB_AUTHORIZATION},
                timeout=settings.REQUESTS_TIMEOUT or 20
            )

            if not result.json()['valid']:
                raise IBANValidatorException(message=result.json()['messages'][0])
        except RequestException as e:
            logger.error("[Validate IBAN] An error occured during request to ESB")
            raise IBANValidatorRequestException from e
        except Exception as e:
            logger.error("[Validate IBAN] An error occured during validation")
            raise IBANValidatorException from e


class IBANValidatorException(Exception):
    def __init__(self, message: str = None):
        self.message = message or "Unable to validate IBAN"
        super().__init__()


class IBANValidatorRequestException(Exception):
    def __init__(self):
        self.message = "An error occured during request to ESB"
        super().__init__()
