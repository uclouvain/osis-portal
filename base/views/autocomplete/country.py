import json

from dal import autocomplete
from django import http

from base.models.academic_year import current_academic_year
from base.utils.api_utils import get_country_list_from_osis


class CountryAutocomplete(autocomplete.Select2ListView):

    def get(self, request, *args, **kwargs):
        return http.HttpResponse(json.dumps({
            'results': [
                {'id': country['uuid'], 'text': country['name']}
                for country in get_country_list_from_osis(
                    search=self.q,
                )['results']
            ]
        }), content_type='application/json')
