import json

from dal import autocomplete
from django import http
from django.conf import settings

from base.views.autocomplete.common import get_list_from_osis


class TrainingAutocomplete(autocomplete.Select2ListView):

    def get(self, request, *args, **kwargs):
        return http.HttpResponse(json.dumps({
            'results': [
                {'id': training['uuid'], 'text': training['acronym'] + " - " + str(training['academic_year'])}
                for training in get_list_from_osis(settings.URL_TRAINING_API, name_filter=self.q)
            ]
        }), content_type='application/json')
