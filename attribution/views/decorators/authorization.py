##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2017 Université catholique de Louvain (http://www.uclouvain.be)
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
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import User
from base import models as mdl_base


def user_is_tutor_or_super_user(function):

    def wrap(request, *args, **kwargs):
        print('user_is_tutor_or_super_user')
        print(kwargs)
        print(kwargs)
        if 'global_id' in kwargs:
            global_id = kwargs['global_id']
        else:
            global_id = args[0]
        a_user = request.user

        if not a_user.is_staff and not a_user.has_perm('base.is_administrator'):
            tutor = mdl_base.tutor.find_by_person_global_id(global_id)
            if tutor.person != mdl_base.person.find_by_user(request.user):
                raise PermissionDenied

        return function(request, *args, **kwargs)

    # wrap.__doc__ = function.__doc__
    # wrap.__name__ = function.__name__
    return wrap
