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
from frontoffice.queue import queue
import json
import performance.models as mdl


class PerformanceConfig(AppConfig):
    name = 'performance'

    def ready(self):
        # if django.core.exceptions.AppRegistryNotReady: Apps aren't loaded yet.
        # ===> This exception says that there is an error in the implementation of method ready(self) !!
        queue.listen_queue(self.name, insert_or_update)


def key_from_json(json):
    """
    Return a key for the json
    :param json: a json object
    :return: a string key
    """
    global_id = json["global_id"]
    academic_year = json["academic_years"][0]["anac"]
    program = json["academic_years"][0]["programs"][0]["program_id"]
    key = "" + global_id + "_" + academic_year + "_" + program
    return key


def insert_or_update(json_data):
    """
        Insert the records in CouchBase. If the records already exist, then the method makes an update.
    """
    data = json.loads(json_data.decode("utf-8"))
    key = key_from_json(data)
    mdl.student_scores.insert_or_update_document(key, data)


