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
from django.conf import settings
from django.core import serializers
from frontoffice.queue import queue_listener
import json
import logging

logger = logging.getLogger(settings.DEFAULT_LOGGER)


class DissertationConfig(AppConfig):
    name = 'dissertation'
    queue_name = 'dissertation_portal'

    def ready(self):
        # if django.core.exceptions.AppRegistryNotReady: Apps aren't loaded yet.
        # ===> This exception says that there is an error in the implementation of method ready(self) !!
        queue_listener.listen_queue(self.queue_name, insert)


def insert(json_data):
    """
    Insert the records in PostGreSQL.
    """
    # Import must be inside the method because django isn't loaded at the launch of the application
    from dissertation import models as mdl_dis

    data = json.loads(json_data.decode("utf-8"))

    class_str = data['model_class_str']
    model_class = map_string_to_model_class(class_str)

    records = data['records']
    if model_class == mdl_dis.adviser.Adviser:
        deserialize_model_data(records, save_model_object)


def deserialize_model_data(data, function_to_apply):
    """
    Deserialize data (see django serialization for the format).
    Json encoding is used.
    :param data: data to be deserialized
    :param function_to_apply: function to apply on the model objects
    :return:
    """
    try:
        for deserialized_object in serializers.deserialize("json", data):
                function_to_apply(deserialized_object)
    except Exception as e:
        logger.error(''.join(['Erreur de deserialisation de : ', str(data)]))
        logger.error(''.join(['Exeption : ', str(e)]))
        pass


def save_model_object(model_object):
    """
    Save a model object. If it already exists in the database, do nothing.
    :param model_object: a model object
    :return:
    """
    model_object.object.save()


def map_string_to_model_class(class_str):
    """
    Map a string to the corresponding model class.
    Returns None if the string cannot be mapped.
    :param class_str: a string corresponding to a mode class
    :return: a model class
    """
    # Import must be inside the method because django isn't loaded at the launch of the application
    from dissertation import models as mdl_dis
    map_classes = {
        'dissertation.adviser.Adviser': mdl_dis.adviser.Adviser
    }
    return map_classes.get(class_str)