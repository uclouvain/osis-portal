##############################################################################
#
# OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2021 Université catholique de Louvain (http://www.uclouvain.be)
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
from django.contrib.auth.models import User
from django.contrib.messages import ERROR
from django.test import TestCase
from django.urls import reverse
from mock import patch

from base.tests.factories.person import PersonFactory
from base.tests.factories.user import UserFactory


class TestInternshipMasterRegistrationView(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.person = PersonFactory(user=None)
        cls.url = reverse('internship_create_account')
        cls.password = 'fake-password'
        cls.account_data = {
            'username': cls.person.email,
            'email': cls.person.email,
            'password1': cls.password,
            'password2': cls.password
        }

    def test_access_registration_page(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'internship_django_registration/registration_form.html')

    def test_access_registration_page_with_email_param(self):
        response = self.client.get(self.url+"?email={}".format(self.person.email))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'internship_django_registration/registration_form.html')
        self.assertEqual(response.context_data['form'].initial['email'], self.person.email)

    @patch(
        'internship.views.internship_authentication.account_activation.'
        'InternshipMasterRegistrationView.get_master_data',
        return_value=None
    )
    def test_post_data_with_non_existing_master_email_address(self, mock_get_master_data):
        response = self.client.post(self.url, data=self.account_data)
        error_message = list(response.wsgi_request._messages)[0]
        self.assertIn(self.person.email, str(error_message))
        self.assertEqual(error_message.level, ERROR)

    @patch(
        'internship.views.internship_authentication.account_activation.'
        'InternshipMasterRegistrationView.get_master_data',
    )
    def test_post_data_with_existing_master_email_address(self, mock_get_master_data):
        mock_get_master_data.return_value = {'person': self.person.__dict__}
        response = self.client.post(self.url, data=self.account_data)
        self.assertTrue(User.objects.get(email=self.person.email))
        self.assertRedirects(response, reverse('internship_master_registration_complete'))

    @patch(
        'internship.views.internship_authentication.account_activation.'
        'InternshipMasterRegistrationView.get_master_data'
    )
    @patch('osis_common.messaging.send_message.send_messages')
    @patch(
        'internship.views.internship_authentication.account_activation.'
        'InternshipMasterRegistrationView.get_activation_key', return_value='ABCD'
    )
    def test_mail_sent_with_activation_link(self, mock_activation_key, mock_send_mail, mock_get_master_data):
        mock_get_master_data.return_value = {'person': self.person.__dict__}
        activation_url = reverse('internship_master_account_activate', kwargs={'activation_key': 'ABCD'})
        self.client.post(self.url, data=self.account_data)
        send_mail_args = mock_send_mail.call_args[0][0]
        self.assertEqual(send_mail_args['receivers'][0]['receiver_email'], self.person.email)
        self.assertIn(activation_url, send_mail_args['template_base_data']['link'])


class TestInternshipMasterRegistrationSuccessView(TestCase):
    def test_access_registration_success_page(self):
        response = self.client.get(reverse('internship_master_registration_complete'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'internship_django_registration/registration_complete.html')


class TestInternshipMasterActivationView(TestCase):
    def setUp(self):
        self.user = UserFactory(is_active=False)
        self.key = 'ABCD'
        self.url = reverse('internship_master_account_activate', kwargs={'activation_key': self.key})

    @patch(
        'internship.views.internship_authentication.account_activation.'
        'InternshipMasterActivationView.trigger_master_activation'
    )
    @patch('internship.views.internship_authentication.account_activation.InternshipMasterActivationView.validate_key')
    def test_activate_user_with_link_trigger_api(self, mock_validate_key, mock_trigger_api_activation):
        mock_validate_key.return_value = self.user.username
        self.client.get(self.url)
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)
        self.assertTrue(mock_trigger_api_activation.called)
