import io
import json

import requests
from dal import autocomplete
from django import http
from django.conf import settings
from rest_framework.parsers import JSONParser


class CountryAutocomplete(autocomplete.Select2ListView):

    def get(self, request, *args, **kwargs):
        return http.HttpResponse(json.dumps({
            'results': [
                {'id': country['uuid'], 'text': country['name']}
                for country in self.get_countries_list(name_filter=self.q)
            ]
        }), content_type='application/json')

    def get_countries_list(self, name_filter=None):
        list_countries = []
        list_country = self.get_country_list_from_osis(name_filter)
        for country in list_country:
            list_countries.append({'uuid': country['uuid'], 'name': country['name']})
        return list_countries

    def get_country_list_from_osis(self, name_filter=None):
        header_to_get = {'Authorization': 'Token ' + settings.OSIS_PORTAL_TOKEN}
        url = settings.URL_COUNTRY_API

        response = requests.get(
            url=url,
            headers=header_to_get,
            data={'search': name_filter or ""}
        )

        stream = io.BytesIO(response.content)
        data = JSONParser().parse(stream)
        if 'results' in data:
            data = data['results']
        return data
