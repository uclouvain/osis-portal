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


###########################################################################
# TO RUN THE SCRIPT ALONE, UNCOMMENT 6 NEXT LINES
# launch "python manage.py shell" in console
# > import frontoffice.osis_migration as osis
# > osis.migrate_base_student() # migration of all students
###########################################################################

from frontoffice.queue import queue_actions
from dissertation.models.adviser import Adviser


def get_all_data(model_class, fields=None, order_by=None):
    """
    Récupère et renvoie tous les records en DB du modèle passé en paramètre.
    :param model_class: La classe du modèle Django (table)
    :param order_by: A string represent the name of a column in the model.
    :return: Liste des records sous forme de dictionnaire
    """
    queryset = model_class.objects
    if fields:
        queryset = queryset.values(*fields)
    else:
        queryset = queryset.values()
    if order_by:
        queryset = queryset.order_by(order_by)
    return list(queryset)  # list() to force the evaluation of the queryset


def get_model_class_str(model_class):
    """
    Recherche la représentation en String (commune à Osis et Osis-portal) pour le modèle passé en paramètre.
    :return: un String qui représente le model_class passé en paramètre.
    """
    map_classes = {


    }
    return map_classes[model_class]


def migrate(model_class, records, queue_name):
    """
    Send all records into the queue name passed in pparameter.
    :param model_class: The model's class used to get data to send into the Queue (to sync these data from Osis to Osis-portal).
    :param queue_name: The name of the queue in which data are sent.
    :param records: List of records to send into the queue.
    """
    data = {
        'model_class_str': get_model_class_str(model_class),
        'records': records,
    }
    queue_actions.send_message(queue_name, data)


def migrate_records(records, model_class, queue_name):
    migrate(model_class, records, queue_name)