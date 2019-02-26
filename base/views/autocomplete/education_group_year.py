import json

from dal import autocomplete
from django import http

from base.models.academic_year import current_academic_year
from base.utils.api_utils import get_training_list_from_osis


class TrainingAutocomplete(autocomplete.Select2ListView):

    def get(self, request, *args, **kwargs):
        return http.HttpResponse(json.dumps({
            'results': [
                {'id': training['uuid'], 'text': training['acronym'] + " - " + str(training['academic_year'])}
                for training in get_training_list_from_osis(
                    search=self.q,
                    from_year=current_academic_year().year+1,
                    to_year=current_academic_year().year+1
                )['results']
            ]
        }), content_type='application/json')
