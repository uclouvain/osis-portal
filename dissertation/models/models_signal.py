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
from django.db.models.signals import post_save
from django.dispatch import receiver
from dissertation.models import adviser
import frontoffice.osis_migration as osis_migration
import sys

queue_name = 'dissertation_osis'


@receiver(post_save, sender=adviser.Adviser)
def on_post_save_dissertation(sender, **kwargs):
    try:
        instance = kwargs["instance"]
        send_instance_to_osis(sender, instance)
    except KeyError:
        pass


def send_instance_to_osis(model_class, instance):
    """
    Send the instance to osis-portal.
    :param model_class: model class of the instance
    :param instance: a model object
    :return:
    """
    # Records contains the serialized instance.
    mod = sys.modules[model_class.__module__]
    # Need to put instance in a list.
    records = mod.serialize_list([instance])
    osis_migration.migrate_records(records=records, model_class=model_class, queue_name=queue_name)