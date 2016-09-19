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
import logging
from django.apps import AppConfig
from django.conf import settings
from django.core import serializers
from frontoffice.queue import queue_listener
from frontoffice.queue import callbacks
import json
from frontoffice.queue.queue_listener import SynchronousConsumerThread

logger = logging.getLogger(settings.DEFAULT_LOGGER)

class BaseConfig(AppConfig):
    name = 'base'
    queue_name = 'osis_base'
    queue_for_migration = 'osis_portal_test' # Data from Osis to insert/update in Osis-portal

    def ready(self):
        try:
            from .models.signals import update_person_after_user_creation, \
                update_person_after_user_update, add_to_students_group
        except ImportError:
            pass
        # if following exception is thrown ; django.core.exceptions.AppRegistryNotReady: Apps aren't loaded yet.
        # ===> This exception says that there is an error anywhere in the implementation of method ready(self) !
        queue_listener.listen_queue(self.queue_name, insert)
        SynchronousConsumerThread(self.queue_for_migration, callbacks.insert_or_update).start()


def insert(json_data):
    """
    Insert the records in PostGreSQL.
    """
    # Import must be inside the method because django isn't loaded at the launch of the application
    from base import models as mdl_base

    data = json.loads(json_data.decode("utf-8"))

    class_str = data['model_class_str']
    model_class = map_string_to_model_class(class_str)

    records = data['records']
    if model_class == mdl_base.student.Student:
        deserialize_model_data(records['persons'], save_model_object)
        deserialize_model_data(records['students'], save_model_object)
    elif model_class == mdl_base.tutor.Tutor:
        deserialize_model_data(records['persons'], save_model_object)
        deserialize_model_data(records['tutors'], save_model_object)


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
    model_object.object.save_from_osis_migration()


def map_string_to_model_class(class_str):
    """
    Map a string to the corresponding model class.
    Returns None if the string cannot be mapped.
    :param class_str: a string corresponding to a mode class
    :return: a model class
    """
    # Import must be inside the method because django isn't loaded at the launch of the application
    from reference import models as mdl_ref
    from base import models as mdl_base
    map_classes = {
        'reference.country.Country': mdl_ref.country.Country,
        'reference.domain.Domain': mdl_ref.domain.Domain,
        'base.tutor.Tutor': mdl_base.tutor.Tutor,
        'base.student.Student': mdl_base.student.Student
    }
    return map_classes.get(class_str)
