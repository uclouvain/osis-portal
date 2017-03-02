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
from django.utils import translation
from django.test import TestCase, override_settings

from admission.forms import applicant as app_forms


class ApplicantFormTest(TestCase):
    def test_error_messages_are_i18n_compliant(self):
        form = app_forms.ApplicantForm()
        first_name_field = form.fields['first_name']
        error_messages = first_name_field.error_messages

        with translation.override('fr-be'):
            self.assertEqual(str(error_messages['required']), 'Champ obligatoire')

        with translation.override('en'):
            self.assertEqual(str(error_messages['required']), 'Mandatory field')
