import requests
from django.conf import settings


def get_list_from_osis(url, **kwargs):
    header_to_get = {'Authorization': 'Token ' + settings.OSIS_PORTAL_TOKEN}
    response = requests.get(
        url=url,
        headers=header_to_get,
        params=kwargs,
    )
    data = response.json()
    return data


def get_country_list_from_osis(**kwargs):
    return get_list_from_osis(settings.URL_COUNTRY_API, **kwargs)


def get_training_list_from_osis(**kwargs):
    return get_list_from_osis(settings.URL_TRAINING_API, **kwargs)
