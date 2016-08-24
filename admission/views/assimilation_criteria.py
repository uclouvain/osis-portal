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


# class JSONResponse(HttpResponse):
#     def __init__(self, data, **kwargs):
#         content = JSONRenderer().render(data)
#         kwargs['content_type'] = 'application/json'
#         super(JSONResponse, self).__init__(content, **kwargs)
#
#
# class AssimilationDocSerializer(serializers.Serializer):
#     description = serializers.CharField(max_length=200)


def find_by_criteria(request):
    criteria = request.GET['criteria']
    list_document_type = []
    if criteria == "1":
        list_document_type = criteria1(list_document_type)
    if criteria == "2":
        list_document_type = criteria2(list_document_type)
    serializer = AssimilationDocSerializer(list_document_type, many=True)

    return JSONResponse(serializer.data)


def criteria1(list_document_type):
        assimilation_doc = AssimilationDoc()
        assimilation_doc.criteria_id = 1
        assimilation_doc.descriptions = [document_type.RESIDENT_LONG_DURATION]
        assimilation_doc.first = True
        list_document_type.append(assimilation_doc)
        assimilation_doc = AssimilationDoc()
        assimilation_doc.criteria_id = 1
        assimilation_doc.descriptions = [document_type.ID_FOREIGN_UNLIMITED]
        list_document_type.append(assimilation_doc)
        return list_document_type


def criteria2(list_document_type):
    assimilation_doc = AssimilationDoc()
    assimilation_doc.criteria_id = 2
    assimilation_doc.descriptions = [document_type.ATTACHMENT_26]
    assimilation_doc.first = True
    list_document_type.append(assimilation_doc)
    assimilation_doc = AssimilationDoc()
    assimilation_doc.criteria_id = 2
    assimilation_doc.descriptions = [document_type.REFUGEE_CARD,
                                     document_type.FAMILY_COMPOSITION,
                                     document_type.BIRTH_CERTIFICATE]
    list_document_type.append(assimilation_doc)
    #
    assimilation_doc = AssimilationDoc()
    assimilation_doc.criteria_id = 2
    assimilation_doc.descriptions = [document_type.REFUGEE_CARD,
                                     document_type.RESIDENT_CERTIFICATE,
                                     document_type.BIRTH_CERTIFICATE]
    list_document_type.append(assimilation_doc)
    #
    assimilation_doc = AssimilationDoc()
    assimilation_doc.criteria_id = 2
    assimilation_doc.descriptions = [document_type.FOREIGN_INSCRIPTION_CERTIFICATE,
                                     document_type.SUBSIDIARY_PROTECTION_DECISION,
                                     document_type.RESIDENCE_PERMIT]
    list_document_type.append(assimilation_doc)
    #
    assimilation_doc = AssimilationDoc()
    assimilation_doc.criteria_id = 2
    assimilation_doc.descriptions = [document_type.STATELESS_CERTIFICATE, ]
    list_document_type.append(assimilation_doc)
    return list_document_type


def find_assimilation_basic_documents():
    """
    Make a list of all the documents possible while encoding assimilation criteria
    List of object with
    :return:
    """
    list_document_type = []
    list_document_type = criteria1(list_document_type)
    list_document_type = criteria2(list_document_type)

    return list_document_type


class AssimilationDoc(object):
    criteria_id = None
    descriptions = None
    first = False

    def __init__(self):
        self.description = None
        self.criteria_id = None
        self.first = False


def find_list_assimilation_basic_documents():
        assimilation_uploads = [
            document_type.RESIDENT_LONG_DURATION,
            document_type.ID_FOREIGN_UNLIMITED,
            document_type.ATTACHMENT_26,
            document_type.REFUGEE_CARD,
            document_type.FAMILY_COMPOSITION,
            document_type.BIRTH_CERTIFICATE,
            document_type.RESIDENT_CERTIFICATE,
            document_type.STATELESS_CERTIFICATE,
            document_type.FOREIGN_INSCRIPTION_CERTIFICATE,
            document_type.SUBSIDIARY_PROTECTION_DECISION,
            document_type.RESIDENCE_PERMIT,
            document_type.PAYCHECK,
            document_type.CPAS,
            document_type.TUTORSHIP_CERTIFICATE,
            document_type.OTHER,
            document_type.SCHOLARSHIP_CFWB,
            document_type.SCHOLARSHIP_DEVELOPMENT_COOPERATION]
        return assimilation_uploads

