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
from rest_framework import serializers
from admission import models as mdl
from django.http import HttpResponse
from rest_framework.renderers import JSONRenderer
from django.views.decorators.csrf import csrf_exempt
from reference import models as mdl_reference

class JSONResponse(HttpResponse):
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)


class EducationInstitutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = mdl_reference.education_institution.EducationInstitution
        fields = ('id', 'name', 'postal_code', 'city', 'country')


@csrf_exempt
def find_by_country(request):
    country = request.GET['country']
    education_institutions = mdl_reference.education_institution.find_by_country(country)
    serializer = EducationInstitutionSerializer(education_institutions, many=True)
    return JSONResponse(serializer.data)


@csrf_exempt
def find_by_city(request):
    city = request.GET['city']
    # country = request.GET['country']

    if city != "-":
        education_institutions = mdl_reference.education_institution.find_by_city(city)
    else:
        education_institutions = mdl_reference.education_institution.find_education_institution_by_adhoc(False)
    serializer = EducationInstitutionSerializer(education_institutions, many=True)
    return JSONResponse(serializer.data)