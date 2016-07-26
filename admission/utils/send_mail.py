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
from django.template import Template, Context
from django.template.loader import render_to_string
from admission.models import message_template as message_template_mdl
from frontoffice.settings import DEFAULT_FROM_EMAIL, LOGO_OSIS_URL, LOGO_EMAIL_SIGNATURE_URL
from frontoffice import settings
from django.utils import translation, timezone
from html import unescape
from django.utils.html import strip_tags
from django.utils.translation import ugettext as _
from admission import models as mdl


def send_mail_activation(request, activation_code, applicant, template_reference):

    sent_error_message = None
    template = message_template_mdl.find_by_reference(template_reference + '_txt')
    txt_message_templates = None
    html_message_templates = None
    if template:
        txt_message_templates = {template.language: template}

    template = message_template_mdl.find_by_reference(template_reference + '_html')
    if template:
        html_message_templates = {template.language: template}

    if not html_message_templates:
        sent_error_message = _('template_error').format(template_reference)
    else:
        activation_link = request.scheme + "://" \
                          + request.get_host() \
                          + "/admission/admission/user/" \
                          + activation_code \
                          + "/activation"
        data = {
            'title': title(applicant.gender),
            'academic_year': mdl.academic_year.current_academic_year(),
            'activation_link': activation_link,
            'signature': render_to_string('email/html_email_signature.html', {
                'logo_mail_signature_url': LOGO_EMAIL_SIGNATURE_URL,
                'logo_osis_url': LOGO_OSIS_URL})
        }
        persons = [applicant]
        dest_by_lang = map_persons_by_languages(persons)
        for lang_code, person in dest_by_lang.items():
                if lang_code in html_message_templates:
                    html_message_template = html_message_templates.get(lang_code)
                else:
                    html_message_template = html_message_templates.get(settings.LANGUAGE_CODE)
                if lang_code in txt_message_templates:
                    txt_message_template = txt_message_templates.get(lang_code)
                else:
                    txt_message_template = txt_message_templates.get(settings.LANGUAGE_CODE)
                with translation.override(lang_code):

                    html_message = Template(html_message_template.template).render(Context(data))
                    subject = html_message_template.subject

                    txt_message = Template(txt_message_template.template).render(Context(data))
                    send(persons=persons,
                         subject=unescape(strip_tags(subject)),
                         message=unescape(strip_tags(txt_message)),
                         html_message=html_message,
                         from_email=DEFAULT_FROM_EMAIL)
    return sent_error_message


def new_password(request, activation_code, email):
    activation_link = request.scheme \
                      + "://" + request.get_host() \
                      + "/admission/admission/new_password_form/" \
                      + activation_code
    subject = 'UCL - Votre code d\'activation pour la modification du mot de passe de votre compte.'
    html_message = ''.join([
        EMAIL_HEADER,
        str('<p>Bonjour, </p>'),
        str('<br><br>'),
        str('Pour modifier votre mot de passe merci de cliquer sur le lien suivant :<br><br>'),
        str('<a href="%s">%s</a>') % (activation_link, activation_link),
        str('<br><br>'),
        str('Le service des inscription de l\'UCL<br><br>'),
        str('<a href=\'http://www.uclouvain.be/inscriptionenligne\'>http://www.uclouvain.be/inscriptionenligne</a>'),
        EMAIL_SIGNATURE,
        EMAIL_FOOTER
    ])

    message = ''.join([
        str('Bonjour, \n\n'),
        str('Pour modifier votre mot de passe merci de cliquer sur le lien suivant :\n\n'),
        str(activation_link),
        str('\n'),
        str('Le service des inscription de l\'UCL\n\n'),
        str('http://www.uclouvain.be/inscriptionenligne')
    ])

    send_mail(subject=subject,
              message=message,
              recipient_list=[email],
              html_message=html_message,
              from_email=DEFAULT_FROM_EMAIL)

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


def map_persons_by_languages(persons):
    """
    Convert a list of persons into a dictionnary langage_code: list_of_emails ,
    according to the language of the person.
    :param persons the list of persons we want to map
    """
    lang_dict = {lang[0]: [] for lang in settings.LANGUAGES}
    for person in persons:
        if person.language in lang_dict.keys():
            lang_dict[person.language].append(person)
        else:
            lang_dict[settings.LANGUAGE_CODE].append(person)
    return lang_dict


def send(persons, **kwargs):
    """
    Send the message :
    - by mail if person.mail exists
    Save the message in message_history table
    :param persons List of the persons to send the message
    :param kwargs List of arguments used by the django send_mail method.
    The recipient_list argument is taken form the persons list.
    """
    recipient_list = []
    if persons:
        for person in persons:
            if person.user.email:
                recipient_list.append(person.user.email)

        send_mail(recipient_list=recipient_list, **kwargs)


def title(gender):
    if gender == "MALE":
        return _('mister')
    if gender == "FEMALE":
        return _('miss')
    return _('miss') + ", " + _('mister')
