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
from rest_framework import serializers
from rest_framework.renderers import JSONRenderer
from admission.models.enums import document_type
import json


class JSONResponse(HttpResponse):
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)


class AssimilationDocSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=200)


def find_by_criteria(request):
    criteria = request.GET['criteria']
    list_document_type = []

    if criteria == "1":
        assimilation_doc = AssimilationDoc()
        assimilation_doc.name = "RESIDENT_LONG_DURATION"
        list_document_type.append(assimilation_doc)
        assimilation_doc = AssimilationDoc()
        assimilation_doc.name = "ID_FOREIGN_UNLIMITED"
        list_document_type.append(assimilation_doc)
    if criteria == "2":
        assimilation_doc = AssimilationDoc()
        assimilation_doc.name = "ATTACHMENT_26"
        list_document_type.append(assimilation_doc)
        assimilation_doc = AssimilationDoc()
        assimilation_doc.name = "REFUGEE_CARD"
        list_document_type.append(assimilation_doc)

    serializer = AssimilationDocSerializer(list_document_type, many=True)

    return JSONResponse(serializer.data)


class AssimilationDoc(object):
    name = None

    def __init__(self):
        self.name = None
