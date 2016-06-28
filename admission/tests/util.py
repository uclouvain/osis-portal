##############################################################################
#
# OSIS stands for Open Student Information System. It's an application
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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
"""
Utility file for Tests units
"""
from django.contrib.auth.models import User
import os

from base.models.person import BasePerson


ADMIN_USER = 'admin_user'
GRANTED_USER = 'granted_user'
VALID_USER = 'valid_user'
INVALID_USER = 'invalid_user'
PASSWORD = 'password'
EMAIL = 'user@osis.org'


def init_admin_user():
    """
    Initialise an Admin user
    """
    user = User.objects.create_superuser(ADMIN_USER, EMAIL, PASSWORD, is_staff=True)
    user.save()


def init_granted_user():
    """
    Initialise a user tha has been granted to acces tested methods.
    If a new authorisation is set for a tested method , it has to be added to the "set_permissions_to_granted" methods.
    """
    user = User.objects.create_user(GRANTED_USER, EMAIL, PASSWORD)
    set_permissions_to_granted(user)
    user.save()


def set_permissions_to_granted(user):
    """
    Grant permissions to the user
    :param user: The user to grant permissions
    """
    return


def init_valid_user():
    """
    Initialise a user that can log in , but doesn't have authorisations to access methods
    """
    user = User.objects.create_user(VALID_USER, EMAIL, PASSWORD)
    user.save()


def init_all_test_users():
    """
    Initialise all user types
    """
    init_admin_user()
    init_granted_user()
    init_valid_user()


def email_destination_person():
    return BasePerson(last_name='Test user', gender='M', email='gaetan.lamarca@uclouvain.be')


def test_if_file_starting_with_exists(starting_with, file_dir_path):
    filenames = os.listdir(file_dir_path)
    for filename in filenames:
        if os.path.isfile(filename) and filename.startswith(starting_with):
            return True
    else:
        return False

