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
from django.dispatch.dispatcher import receiver
from base.models.person import find_by_global_id, find_by_user, Person

try:
    from osis_louvain_auth.authentication.shibboleth_auth import user_updated_signal, user_created_signal

    @receiver(user_updated_signal, user_created_signal)
    def update_person_from_user(sender, **kwargs):
        user = kwargs.get('user')
        user_infos = kwargs.get('user_infos')
        person = find_by_global_id(user_infos.get('USER_FGS'))
        if not person:
            person = find_by_user(user)
        if not person:
            person = Person(user=user,
                            global_id=user_infos.get('USER_FGS'),
                            first_name=user_infos.get('USER_FIRST_NAME'),
                            last_name=user_infos.get('USER_LAST_NAME'),
                            email=user_infos.get('USER_EMAIL'))
        else:
            person.user = user
            person.first_name = user.first_name
            person.last_name = user.last_name
            person.email = user.email
            person.global_id = user_infos.get('USER_FGS')
        person.save()
        return person

except Exception:
    pass


