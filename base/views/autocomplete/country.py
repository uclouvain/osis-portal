import json

from dal import autocomplete
from django import http

from base.views.autocomplete.common import get_country_list_from_osis


class CountryAutocomplete(autocomplete.Select2ListView):

    def get(self, request, *args, **kwargs):
        return http.HttpResponse(json.dumps({
            'results': [
                {'id': country['uuid'], 'text': country['name']}
                for country in get_country_list_from_osis(name_filter=self.q)
            ]
        }), content_type='application/json')
