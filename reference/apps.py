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
from django.apps import AppConfig
from frontoffice import queue
import json



class ReferenceConfig(AppConfig):
    name = 'reference'

    def insert_or_update(self, json_datas):
        """
        Insert the records in PostGreSQL. If the records already exist, then the method makes an update.
        """
        data = json.loads(json_datas.decode("utf-8"))
        from reference import models
        map_classes = {
            'reference.Country': models.Country,
        }
        cls_str = data['model_class_str']
        model_class = map_classes[cls_str]
        records = data['records']
        # ids = [obj['id'] for obj in records]
        for record in records :
            obj, created = model_class.objects.update_or_create(defaults=record, **{'id' : record['id']})
            print("created ? : " + str(created))

    def ready(self):
        # if django.core.exceptions.AppRegistryNotReady: Apps aren't loaded yet.
        # ===> This exception says that there is an error in the implementation of method ready(self) !!
        queue.listen_queue(self.name, self.insert_or_update)
