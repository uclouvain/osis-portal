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

import json

from django.core import serializers
from django.db.models import ForeignKey


def insert_or_update(json_data):
    # records = json.loads(json_data.decode("utf-8"))
    # list_fields = get_model_fields(model_class)
    # records = data['records']
    instances = serializers.deserialize('json', json_data, ignorenonexistent=True)
    for instance in instances:
        instance.save()

#
# def insert_or_update(json_data):
#     """
#     Insert the records in PostGreSQL. If the records already exist, then the method makes an update.
#     """
#     data = json.loads(json_data.decode("utf-8"))
#     # Import must be inside the method because django isn't loaded at the launch of the application
#     from reference import models as mdl_ref
#     from base import models as mdl_base
#     map_classes = {
#         'reference.assimilation_criteria.AssimilationCriteria': mdl_ref.assimilation_criteria.AssimilationCriteria,
#         'reference.country.Country': mdl_ref.country.Country,
#         'reference.decree.Decree': mdl_ref.decree.Decree,
#         'reference.domain.Domain': mdl_ref.domain.Domain,
#         'reference.education_institution.EducationInstitution': mdl_ref.education_institution.EducationInstitution,
#         'reference.education_type.EducationType': mdl_ref.education_type.EducationType,
#         'reference.external_offer.ExternalOffer': mdl_ref.external_offer.ExternalOffer,
#         'reference.grade_type.GradeType': mdl_ref.grade_type.GradeType,
#         'reference.institutional_grade_type.InstitutionalGradeType': mdl_ref.institutional_grade_type.InstitutionalGradeType,
#         'reference.language.Language': mdl_ref.language.Language,
#         'base.campus.Campus': mdl_base.campus.Campus,
#         'base.offer.Offer': mdl_base.offer.Offer,
#         'base.offer_year.OfferYear': base.models.offer_year.OfferYear,
#         'base.offer_enrollment.OfferEnrollment': mdl_base.offer_enrollment.OfferEnrollment,
#         'base.organization.Organization': mdl_base.organization.Organization,
#         'base.student.Student': mdl_base.student.Student,
#         'base.tutor.Tutor': mdl_base.tutor.Tutor,
#
#     }
#     cls_str = data['model_class_str']
#     model_class = map_classes[cls_str]
#     # records = serializers.deserialize("json", data['records'])
#     records = data['records']
#     if model_class == mdl_base.tutor.Tutor or model_class == mdl_base.student.Student:  # Special case
#         for instance in serializers.deserialize('json', records):
#             instance.save()
#     else:
#         for record in records:
#             list_fields = get_model_fields(model_class)
#             new_record = remove_non_existent_fields(list_fields, record)
#             model_class.objects.update_or_create(id=new_record['id'], defaults=new_record)
#             # create_or_update(model_class, record)
#
#
# def create_or_update(model_class, record):
#     """
#     Create or update the database based on the record.
#     :param model_class: a model
#     :param record: a dictionary where each key is a field of the model
#     :return: the created obj
#     """
#     list_fields = get_model_fields(model_class)
#     new_record = remove_non_existent_fields(list_fields, record)
#     external_id = new_record.get('external_id', None)
#
#     if external_id is None:  # then object was not created created on osis-portal
#         received_id = new_record.pop('id')  # !! should never update id value
#         new_record['external_id'] = received_id
#         obj, created = model_class.objects.update_or_create(external_id=received_id,
#                                                             defaults=new_record)
#
#     else:                   # the object was originaly created on osis-portal
#         external_id = new_record.pop('external_id')
#         del new_record['id']  # !! should never update id value
#         obj, created = model_class.objects.update_or_create(id=external_id,
#                                                             defaults=new_record)  # should always do an update
#     return obj
#
#
# def remove_non_existent_fields(list_fields, record):
#     """
#     Remove all the fields that are inexistent from the record.
#     :param list_fields: a list of string where each string corresponds to a model field
#     :param record: a dictionary where each key correspond to a field name
#     :return: a modified record
#     """
#     record_copy = record.copy()
#     for key in record.keys():
#         if key not in list_fields:
#             del record_copy[key]
#     return record_copy
#
#
# def get_model_fields(model_class):
#     """
#     Return a list of fields for a given model class.
#     :param model_class: a django model
#     :return: a list of string where each string corresponds to a model field
#     """
#     fields = [field for field in model_class._meta.fields]
#     field_names = []
#     for f in fields:
#         if isinstance(f, ForeignKey):
#             field_names.append(f.name + '_id')
#         else:
#             field_names.append(f.name)
#     return field_names
