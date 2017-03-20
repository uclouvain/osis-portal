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
from django.conf.urls import url
from base.views import administration, my_osis

urlpatterns = [
    url(r'^'+settings.ADMIN_URL+'data/$', administration.data, name='data'),
    url(r'^my_osis/$', my_osis.my_osis_index, name="my_osis"),
#     url(r'^my_osis/management_tasks/messages_templates', my_osis.messages_templates_index, name="messages_templates"),
#     url(r'^my_osis/my_messages/$', my_osis.my_messages_index, name="my_messages"),
#     url(r'^my_osis/my_messages/action/$', my_osis.my_messages_action, name="my_messages_action"),
#     url(r'^my_osis/my_messages/read/([0-9]+)/$', my_osis.read_message, name="read_my_message"),
#     url(r'^my_osis/my_messages/delete/([0-9]+)/$', my_osis.delete_from_my_messages, name="delete_my_message"),
#     url(r'^my_osis/my_messages/send_message_again/([0-9]+)/$', my_osis.send_message_again,
#         name='send_message_again'),
#     url(r'^my_osis/profile/$', my_osis.profile, name='profile'),
    url(r'^my_osis/profile/lang$', my_osis.profile_lang, name='profile_lang'),
]
