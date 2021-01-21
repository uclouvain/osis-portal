from django.conf import settings
import osis_attribution_sdk
from django.core.exceptions import ImproperlyConfigured

from base.models.person import Person


def build_configuration(person: Person = None) -> osis_attribution_sdk.Configuration:
    """
    Return SDK configuration of attribution based on person provided in kwargs
    If no person provided, it will use generic token to make request
    """
    if not settings.OSIS_ATTRIBUTION_SDK_HOST:
        raise ImproperlyConfigured('OSIS_ATTRIBUTION_SDK_HOST must be set in configuration')

    if person is None:
        token = settings.OSIS_PORTAL_TOKEN
    else:
        # TODO : Move logic (api.get_token_from_osis) to shared utility class
        from continuing_education.views import api
        token = api.get_token_from_osis(person.user)

    return osis_attribution_sdk.Configuration(
        host=settings.OSIS_ATTRIBUTION_SDK_HOST,
        api_key={
            'Token': token
        })
