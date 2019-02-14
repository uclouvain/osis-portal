import json

from dal import autocomplete
from django import http

from continuing_education.views.common import get_countries_list


class CountryAutocomplete(autocomplete.Select2ListView):

    def get_list(self):
        countries_list = get_countries_list()
        return countries_list

    def get(self, request, *args, **kwargs):
        """"Return option list json response."""
        results = self.get_list()

        if self.q:
            results = [x for x in get_countries_list(name_filter=self.q) if self.q.lower() in x.lower()]

        return http.HttpResponse(json.dumps({
            'results': [dict(id=x, text=x) for x in results]
        }), content_type='application/json')
