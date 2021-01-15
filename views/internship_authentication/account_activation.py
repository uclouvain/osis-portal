##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.contrib.sites.shortcuts import get_current_site
from django.core import signing
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy, reverse
from django.utils.encoding import force_text
from django.utils.translation import gettext as _
from django.views.generic import TemplateView
from django_registration import signals
from django_registration.exceptions import ActivationError
from django_registration.forms import RegistrationFormUniqueEmail
from django_registration.views import RegistrationView, ActivationView

from internship.views.api_client import InternshipAPIClient
from osis_common.messaging import message_config, send_message

REGISTRATION_SALT = getattr(settings, 'REGISTRATION_SALT', 'registration')


class InternshipMasterRegistrationForm(RegistrationFormUniqueEmail):
    def __init__(self, *args, **kwargs):
        super(InternshipMasterRegistrationForm, self).__init__(*args, **kwargs)
        self.fields['email'].widget.attrs['readonly'] = True


class InternshipMasterRegistrationView(RegistrationView):
    template_name = 'internship_django_registration/registration_form.html'
    success_url = reverse_lazy('internship_master_registration_complete')
    form_class = InternshipMasterRegistrationForm
    html_template_ref = 'internship_master_account_activation_html'
    txt_template_ref = 'internship_master_account_activation_txt'
    master = None

    def get(self, request, *args, **kwargs):
        self.initial = {'email': request.GET.get('email', '')}
        return super().get(self, request, *args, **kwargs)

    def form_valid(self, form):
        email = form.cleaned_data['username']
        self.master = self.get_master_data(email)
        if self.master:
            return HttpResponseRedirect(self.get_success_url(self.register(form)))
        master_registration_error_msg = _('Internship master with email {} does not exist'.format(email))
        messages.add_message(self.request, messages.ERROR, master_registration_error_msg)
        return super(RegistrationView, self).render_to_response(context=self.get_context_data())

    def register(self, form):
        new_user = self.create_user(form)
        signals.user_registered.send(
            sender=self.__class__,
            user=new_user,
            request=self.request
        )
        self.send_activation_email(new_user)
        return new_user

    def create_user(self, form):
        """
        Create the user account
        """
        new_user = form.save(commit=False)
        new_user.first_name = self.master['person']['first_name']
        new_user.last_name = self.master['person']['last_name']
        new_user.is_active = False
        new_user.save()
        return new_user

    def get_master_data(self, email):
        master = InternshipAPIClient().masters_get(search=email)
        if master['count'] != 0:
            return master['results'][0]
        return None

    @staticmethod
    def get_activation_key(user):
        """
        Generate the activation key which will be emailed to the user.

        """
        return signing.dumps(
            obj=user.get_username(),
            salt=REGISTRATION_SALT
        )

    def __get_activation_link(self, activation_key):
        scheme = 'https' if self.request.is_secure() else 'http'
        site = get_current_site(self.request)
        params = {'activation_key': activation_key}
        url = reverse('internship_master_account_activate', kwargs=params)
        return '{scheme}://{site}{url}'.format(scheme=scheme, site=site, url=url)

    def send_activation_email(self, user):
        """
        Send the activation email. The activation key is the username,
        signed using TimestampSigner.

        """
        activation_key = self.get_activation_key(user)
        receivers = [message_config.create_receiver(user.id, user.email, None)]

        template_base_data = {
            'link': self.__get_activation_link(activation_key),

        }
        message_content = message_config.create_message_content(
            self.html_template_ref,
            self.txt_template_ref,
            [],
            receivers,
            template_base_data,
            None
        )
        send_message.send_messages(message_content)


class InternshipMasterRegistrationSuccessView(TemplateView):
    template_name = 'internship_django_registration/registration_complete.html'


class InternshipMasterActivationView(ActivationView):
    """
    Given a valid activation key, activate the user's
    account. Otherwise, show an error message stating the account
    couldn't be activated.

    """
    ALREADY_ACTIVATED_MESSAGE = _(
        u'The account you tried to activate has already been activated.'
    )
    BAD_USERNAME_MESSAGE = _(
        u'The account you attempted to activate is invalid.'
    )
    EXPIRED_MESSAGE = _(u'This account has expired.')
    INVALID_KEY_MESSAGE = _(
        u'The activation key you provided is invalid.'
    )
    success_url = None

    def activate(self, *args, **kwargs):
        username = self.validate_key(kwargs.get('activation_key'))
        user = self.get_user(username)
        user.is_active = True
        user.save()
        self.trigger_master_activation(user.email)
        return user

    def trigger_master_activation(self, email):
        master = InternshipAPIClient().masters_get(search=email)
        if master['count'] != 0:
            uuid = master['results'][0]['uuid']
            InternshipAPIClient().masters_uuid_activate_account_put(uuid=uuid)

    def validate_key(self, activation_key):
        """
        Verify that the activation key is valid and within the
        permitted activation time window, returning the username if
        valid or raising ``ActivationError`` if not.

        """
        try:
            username = signing.loads(
                activation_key,
                salt=REGISTRATION_SALT,
                max_age=settings.ACCOUNT_ACTIVATION_DAYS * 86400
            )
            return username
        except signing.SignatureExpired:
            raise ActivationError(
                self.EXPIRED_MESSAGE,
                code='expired'
            )
        except signing.BadSignature:
            raise ActivationError(
                self.INVALID_KEY_MESSAGE,
                code='invalid_key',
                params={'activation_key': activation_key}
            )

    def get_user(self, username):
        """
        Given the verified username, look up and return the
        corresponding user account if it exists, or raising
        ``ActivationError`` if it doesn't.

        """
        User = get_user_model()
        try:
            user = User.objects.get(**{
                User.USERNAME_FIELD: username,
            })
            if user.is_active:
                raise ActivationError(
                    self.ALREADY_ACTIVATED_MESSAGE,
                    code='already_activated'
                )
            return user
        except User.DoesNotExist:
            raise ActivationError(
                self.BAD_USERNAME_MESSAGE,
                code='bad_username'
            )

    def get(self, *args, **kwargs):
        """
        The base activation logic; subclasses should leave this method
        alone and implement activate(), which is called from this
        method.

        """
        extra_context = {}
        try:
            activated_user = self.activate(*args, **kwargs)
        except ActivationError as e:
            extra_context['activation_error'] = {
                'message': e.message,
                'code': e.code,
                'params': e.params
            }
        else:
            signals.user_activated.send(
                sender=self.__class__,
                user=activated_user,
                request=self.request
            )
            login(self.request, activated_user, backend='django.contrib.auth.backends.ModelBackend')
            return HttpResponseRedirect(
                force_text(
                    self.get_success_url(activated_user)
                )
            )
        context_data = self.get_context_data()
        context_data.update(extra_context)
        return self.render_to_response(context_data)

    def get_success_url(self, user=None):
        if not user:
            raise ActivationError(
                self.BAD_USERNAME_MESSAGE,
                code='bad_username'
            )
        return force_text(reverse("internship_score_encoding"))
