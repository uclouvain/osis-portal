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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################

from osis_common.messaging import message_config, send_message as message_service


def send_mail_to_teacher_new_dissert(adviser):
    """
    Notify (for the teacher) of a new dissertation project
    """
    html_template_ref = 'dissertation_adviser_new_project_dissertation_html'
    txt_template_ref = 'dissertation_adviser_new_project_dissertation_txt'
    receivers = [message_config.create_receiver(adviser.person.id, adviser.person.email, adviser.person.language)]
    suject_data = None
    template_base_data = {'adviser': adviser, }
    tables = None
    message_content = message_config.create_message_content(html_template_ref, txt_template_ref, tables, receivers, template_base_data, suject_data)
    return message_service.send_messages(message_content)
