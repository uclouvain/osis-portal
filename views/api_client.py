from django.conf import settings
from osis_internship_sdk.api.default_api import DefaultApi
from osis_internship_sdk.api_client import ApiClient
from osis_internship_sdk.configuration import Configuration


class InternshipAPIClient:

    def __new__(cls):
        api_config = Configuration()
        api_config.api_key['Authorization'] = "Token "+settings.OSIS_PORTAL_TOKEN
        api_config.host = settings.URL_INTERNSHIP_API
        return DefaultApi(api_client=ApiClient(configuration=api_config))
