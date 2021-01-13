from django.conf import settings

from internship.openapi_client.api.default_api import DefaultApi
from internship.openapi_client.api_client import ApiClient
from internship.openapi_client.configuration import Configuration


class InternshipAPIClient:

    def __new__(cls):
        api_config = Configuration()
        api_config.api_key['Authorization'] = "Token "+settings.OSIS_PORTAL_TOKEN
        api_config.host = settings.URL_INTERNSHIP_API
        return DefaultApi(api_client=ApiClient(configuration=api_config))
