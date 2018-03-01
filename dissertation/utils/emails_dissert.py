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
from dissertation.models import dissertation_role


def get_base_template(dissert):
    template_base_data = {'author': dissert.author,
                          'title': dissert.title,
                          'promoteur': create_string_list_promoteurs(dissert),
                          'description': dissert.description,
                          'dissertation_proposition_titre': dissert.proposition_dissertation.title}
    return template_base_data


def create_string_list_promoteurs(dissert):
    liste_promoteurs_string = ''
    promoteurs = dissertation_role.find_all_promoteur_by_dissertation(dissert)
    if promoteurs:
        liste_promoteurs_string = ','.join(['{} {}'.format(dissrole.adviser.person.first_name,
                                            dissrole.adviser.person.last_name)
                                            for dissrole in promoteurs])
    return liste_promoteurs_string


def send_email_to_all_promoteurs(dissert, template):
    print('___'+ str(dissertation_role.find_all_promoteur_by_dissertation(dissert)))
    receivers = [diss_role.adviser for diss_role in dissertation_role.find_all_promoteur_by_dissertation(dissert)]
    send_email(dissert, template, receivers)


def send_email(dissert, template_ref, receivers):
    receivers = generate_receivers(receivers)
    html_template_ref = template_ref + '_html'
    txt_template_ref = template_ref + '_txt'
    suject_data = None
    template_base_data = get_base_template(dissert)
    tables = None
    message_content = message_config.create_message_content(html_template_ref, txt_template_ref, tables, receivers,
                                                            template_base_data, suject_data)
    return message_service.send_messages(message_content)


def generate_receivers(receivers):
    receivers_tab = []
    for receiver in receivers:
        receivers_tab.append(message_config.create_receiver(receiver.person.id,
                                                            receiver.person.email,
                                                            receiver.person.language))
    return receivers_tab
