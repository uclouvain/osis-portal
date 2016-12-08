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
from django.contrib.auth.models import Group
from django.db.models.signals import post_save, post_delete
from django.dispatch.dispatcher import receiver, Signal
from base.models import student, tutor
from base.models.person import find_by_global_id, find_by_user, Person
from base.models.student import Student
from base.models.tutor import Tutor
from osis_common.models.serializable_model import SerializableModel

person_created = Signal(providing_args=['person'])

try:
    from osis_louvain_auth.authentication.shibboleth_auth import user_updated_signal, user_created_signal

    @receiver(user_created_signal)
    def update_person_after_user_creation(sender, **kwargs):
        user = kwargs.get('user')
        user_infos = kwargs.get('user_infos')
        person = find_by_global_id(user_infos.get('USER_FGS'))
        person = _create_update_person(user, person, user_infos)
        _add_person_to_group(person)
        return person

    @receiver(user_updated_signal)
    def update_person_after_user_update(sender, **kwargs):
        user = kwargs.get('user')
        user_infos = kwargs.get('user_infos')
        person = find_by_global_id(user_infos.get('USER_FGS'))
        person = _create_update_person(user, person, user_infos)
        return person


except Exception:
    pass


@receiver(post_save, sender=Student)
def add_to_students_group(sender, instance, **kwargs):
    if kwargs.get('created', True) and instance.person.user:
        _assign_group(instance.person, "students")


@receiver(post_save, sender=Tutor)
def add_to_tutors_group(sender, instance, **kwargs):
    if kwargs.get('created', True) and instance.person.user:
        _assign_group(instance.person, "tutors")


@receiver(post_delete, sender=Tutor)
def remove_from_tutor_group(sender, instance, **kwargs):
    if instance.person.user:
        tutors_group = Group.objects.get(name='tutors')
        instance.person.user.groups.remove(tutors_group)


@receiver(post_delete, sender=Student)
def remove_from_student_group(sender, instance, **kwargs):
    if instance.person.user:
        students_group = Group.objects.get(name='students')
        instance.person.user.groups.remove(students_group)


def _add_person_to_group(person):
    # Check Student
    if student.find_by_person(person):
        _assign_group(person, "students")
    # Check tutor
    if tutor.find_by_person(person):
        _assign_group(person, "tutors")


def _assign_group(person, group_name):
    """
    Assign the "person" to the group named "group_name"
    :param person: != none, an object person
    :param group_name: a string of a legit group
    :return: nothing
    """
    group = Group.objects.get(name=group_name)
    if person.user and \
            not person.user.groups.filter(name=group_name).exists():
        person.user.groups.add(group)


def _create_update_person(user, person, user_infos):
    if not person:
        person = find_by_user(user)
    if not person:
        person = Person(user=user,
                        global_id=user_infos.get('USER_FGS'),
                        first_name=user_infos.get('USER_FIRST_NAME'),
                        last_name=user_infos.get('USER_LAST_NAME'),
                        email=user_infos.get('USER_EMAIL'))
        person.save()
        person_created.send(sender=None, person=person)
    else:
        updated, person = _update_person_if_necessary(person, user, user_infos.get('USER_FGS'))
    return person


def _update_person_if_necessary(person, user, global_id):
    updated = False
    if user:
        if user != person.user:
            person.user = user
            updated = True
        if user.first_name and person.first_name != user.first_name:
            person.first_name = user.first_name
            updated = True
        if user.last_name and person.last_name != user.last_name:
            person.last_name = user.last_name
            updated = True
        if user.email and person.email != user.email:
            person.email = user.email
            updated = True
    if global_id and person.global_id != global_id:
        person.global_id = global_id
        updated = True
    if updated:
        super(SerializableModel, person).save()
    return updated, person

