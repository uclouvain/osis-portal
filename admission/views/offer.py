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
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.renderers import JSONRenderer

from reference import models as mdl_reference
from base import models as mdl_base


class JSONResponse(HttpResponse):
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)


class OfferSerializer(serializers.ModelSerializer):
    institutional_grade_type = serializers.SerializerMethodField('get_grade_type')

    class Meta:
        model = mdl_base.offer_year.OfferYear
        fields = ('id', 'acronym', 'title', 'title_international', 'grade_type', 'subject_to_quota',
                  'institutional_grade_type')

    def get_grade_type(self, obj):
        return obj.grade_type.institutional_grade_type


def search(request):
    grade_type = request.GET['grade_type']
    domain = request.GET['domain']
    serializer = OfferSerializer([], many=True)
    if grade_type != 'undefined' and domain != 'undefined':
        offer_year_domains = mdl_base.offer_year_domain.search(grade_type, domain)
        list_offer_years = []
        for offer_year_domain in offer_year_domains:
            list_offer_years.append(offer_year_domain.offer_year)
        serializer = OfferSerializer(list_offer_years, many=True)
    return JSONResponse(serializer.data)


def find_by_id(request):
    offer_year_id = request.GET['offer']
    offer_year = mdl_base.offer_year.find_by_id(offer_year_id)
    serializer = OfferSerializer(offer_year)
    return JSONResponse(serializer.data)


def _get_offer_type(request):
    offer_type = None

    if request.POST.get('bachelor_type'):
        offer_type = request.POST['bachelor_type']
    if request.POST.get('master_type'):
        offer_type = request.POST['master_type']
    if request.POST.get('doctorate_type'):
        offer_type = request.POST['doctorate_type']
    if offer_type:
        return get_object_or_404(mdl_reference.grade_type.GradeType, pk=offer_type)
    return None


def _get_domain(request):
    domain_id = request.POST.get('domain')
    domain = None
    if domain_id:
        domain = get_object_or_404(mdl_reference.domain.Domain, pk=domain_id)
    return domain
