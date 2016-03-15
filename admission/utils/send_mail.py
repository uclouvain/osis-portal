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

"""
Utility files for mail sending
"""
from django.core.mail import send_mail

from frontoffice.settings import DEFAULT_FROM_EMAIL


def send_mail_activation(request, activation_code, email):
    """
    Send an email to user after  subscription to osis-portal.  Email needed for the subscription activation
    :param request:
    :param activation_code:
    :param email:
    """
    activation_link = request.scheme + "://" + request.get_host() + "/admission/activation/"+ activation_code

    subject = 'UCL - Votre code d\'activation de compte.'
    html_message = ''.join([
        EMAIL_HEADER,
        str('<p>Bonjour, </p>'),
        str('<br>'),
        str('<p>Vous venez d\'introduire une demande de création d\'un compte pour accéder à la demande d\'inscription '
            'en ligne 2015-2016 de l\'Université catholique de Louvain, ce dont nous vous remercions </p><br>'),
        str('Pour activer ce compte, veuillez cliquer sur le lien suivant :<br><br>' ),
        str('<a href="%s">%s</a>') % (activation_link,activation_link),
        str('<br><br>' ),
        str('Le service des inscription de l\'UCL<br><br>' ),
        str('<a href=\'http://www.uclouvain.be/inscriptionenligne\'>http://www.uclouvain.be/inscriptionenligne</a>'),
        EMAIL_SIGNATURE,
        EMAIL_FOOTER
    ])
    message = ''.join([
        str('Bonjour, \n'),
        str('Vous venez d\'introduire une demande de création d\'un compte pour accéder à la demande d\'inscription '
            'en ligne 2015-2016 de l\'Université catholique de Louvain, ce dont nous vous remercions .\n\n'),
        str('Pour activer ce compte, veuillez cliquer sur le lien suivant :\n\n'),
        str(activation_link),
        str('\n'),
        str('Le service des inscription de l\'UCL\n\n' ),
        str('http://www.uclouvain.be/inscriptionenligne')
    ])

    send_mail(subject=subject,message=message,recipient_list=[email],html_message=html_message,from_email=DEFAULT_FROM_EMAIL)


EMAIL_HEADER = """
<html>
    <head>
        <meta http-equiv="Content-Type" content="text/html;charset=iso-8859-1"><title>signature</title>
    </head>
    <body>
"""

EMAIL_SIGNATURE = """

        <table cellpadding="5" cellspacing="5">
            <tbody>
                <tr>
                    <td width="60">
                        <img src="http://www.uclouvain.be/cps/ucl/doc/ac-arec/images/logo-signature.png">
                    </td>
                    <td>
                        <img src="https://osis.uclouvain.be/static/img/logo_osis.png">
                    </td>
                </tr>
            </tbody>
        </table>

"""

EMAIL_FOOTER = """
    </body>
</html>
"""