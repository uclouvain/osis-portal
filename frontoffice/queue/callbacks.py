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

from django.core import serializers
import json


def insert_or_update(json_data):
    """
    Insert the records in PostGreSQL. If the records already exist, then the method makes an update.
    """
    data = json.loads(json_data.decode("utf-8"))
    # Import must be inside the method because django isn't loaded at the launch of the application
    from reference import models as mdl_ref
    from base import models as mdl_base
    map_classes = {
        'reference.Country': mdl_ref.country.Country,
        'reference.Domain': mdl_ref.domain.Domain,
        'reference.EducationInstitution': mdl_ref.education_institution.EducationInstitution,
        'reference.Language': mdl_ref.language.Language,
        'base.Tutor': mdl_base.tutor.Tutor,
        'base.Student': mdl_base.student.Student
    }
    cls_str = data['model_class_str']
    model_class = map_classes[cls_str]
    records = data['records']
    for instance in serializers.deserialize('json', records):
        instance.save()

