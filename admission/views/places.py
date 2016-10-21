##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2016 Université catholique de Louvain (http://www.uclouvain.be)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################

from reference import models as mdl_reference
from django.http import HttpResponse
from rest_framework.renderers import JSONRenderer


class JSONResponse(HttpResponse):
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)


def find_postal_codes_by_city(request):
    city_name = request.GET['city']
    education_institutions = mdl_reference.education_institution.search('BE', 'SECONDARY', False, city_name, None)
    postal_codes = []
    postal_codes_data = []
    for education_institution in education_institutions:

        if education_institution.postal_code not in postal_codes:
            postal_codes.append(education_institution.postal_code)
            postal_codes_data.append({"postal_code": education_institution.postal_code})
    return JSONResponse(postal_codes_data)


def find_cities_by_postal_code(request):
    postal_code = request.GET['postal_code']
    education_institutions = mdl_reference.education_institution.find_cities('BE', 'SECONDARY', False, postal_code)
    cities_data = []
    for education_institution in education_institutions:
        cities_data.append({"city": education_institution.city})
    return JSONResponse(cities_data)