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
from django.conf import settings
from django.contrib.auth.models import Group
from django.db.models.signals import post_save, post_delete
from django.dispatch.dispatcher import receiver, Signal
from django.core.exceptions import ObjectDoesNotExist
from base import models as mdl
from osis_common.models.serializable_model import SerializableModel
from osis_common.models.signals.authentication import user_created_signal, user_updated_signal

person_created = Signal(providing_args=['person'])

GROUP_STUDENTS = "students"
GROUP_STUDENTS_INTERNSHIP = "internship_students"
GROUP_TUTORS = "tutors"


@receiver(user_created_signal)
@receiver(user_updated_signal)
def update_person(sender, **kwargs):
    user = kwargs.get('user')
    user_infos = kwargs.get('user_infos')
    person = mdl.person.find_by_global_id(user_infos.get('USER_FGS'))
    person = _create_update_person(user, person, user_infos)
    _add_person_to_group(person)
    return person


@receiver(post_save, sender=mdl.student.Student)
def add_to_students_group(sender, instance, **kwargs):
    if kwargs.get('created', True) and instance.person.user:
        _assign_group(instance.person, GROUP_STUDENTS)


@receiver(post_save, sender=mdl.tutor.Tutor)
def add_to_tutors_group(sender, instance, **kwargs):
    if kwargs.get('created', True) and instance.person.user:
        _assign_group(instance.person, GROUP_TUTORS)


@receiver(post_delete, sender=mdl.tutor.Tutor)
def remove_from_tutor_group(sender, instance, **kwargs):
    if instance.person.user:
        tutors_group = Group.objects.get(name=GROUP_TUTORS)
        instance.person.user.groups.remove(tutors_group)


@receiver(post_delete, sender=mdl.student.Student)
def remove_from_student_group(sender, instance, **kwargs):
    if instance.person.user:
        students_group = Group.objects.get(name=GROUP_STUDENTS)
        instance.person.user.groups.remove(students_group)


# Internship receivers are defined only if internship app is installed
if 'internship' in settings.INSTALLED_APPS:
    from internship.models import internship_student_information as mdl_internship

    @receiver(post_save, sender=mdl_internship.InternshipStudentInformation)
    def add_to_internship_students_group(sender, instance, **kwargs):
        if kwargs.get('created', True) and instance.person.user:
            _assign_group(instance.person, GROUP_STUDENTS_INTERNSHIP)


    @receiver(post_delete, sender=mdl_internship.InternshipStudentInformation)
    def remove_internship_students_group(sender, instance, **kwargs):
        if instance.person.user:
            internship_students_group = Group.objects.get(name=GROUP_STUDENTS_INTERNSHIP)
            instance.person.user.groups.remove(internship_students_group)


def _add_person_to_group(person):
    # Check Student
    if mdl.student.find_by_person(person):
        _assign_group(person, GROUP_STUDENTS)
    # Check tutor
    if mdl.tutor.find_by_person(person):
        _assign_group(person, GROUP_TUTORS)
    # Check if student is internship student
    # Only if internship app is installed
    if 'internship' in settings.INSTALLED_APPS and mdl_internship.exists_by_person(person):
        _assign_group(person, GROUP_STUDENTS_INTERNSHIP)


def _assign_group(person, group_name):
    """
    Assign the "person" to the group named "group_name"
    :param person: != none, an object person
    :param group_name: a string of a legit group
    :return: nothing
    """
    try:
        group = Group.objects.get(name=group_name)
        if person.user and not person.user.groups.filter(name=group_name).exists():
            person.user.groups.add(group)
    except ObjectDoesNotExist:
        return


def _create_update_person(user, person, user_infos):
    if not person:
        person = mdl.person.find_by_user(user)
    if not person:
        person = mdl.person.Person(user=user,
                                   global_id=user_infos.get('USER_FGS'),
                                   first_name=user_infos.get('USER_FIRST_NAME'),
                                   last_name=user_infos.get('USER_LAST_NAME'),
                                   email=user_infos.get('USER_EMAIL'),
                                   external_id=settings.PERSON_EXTERNAL_ID_PATTERN.format(
                                       global_id=user_infos.get('USER_FGS')))
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
