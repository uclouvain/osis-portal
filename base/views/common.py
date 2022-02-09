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
from typing import List

from django.conf import settings
from django.contrib.auth import authenticate, logout
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect

from base.models import person as person_mdl
from base.views import layout, api
from osis_common.models import application_notice


def return_error_response(request, template, status_code):
    response = layout.render(request, template, {})
    response.status_code = status_code
    return response


def page_not_found(request, *args, **kwargs):
    return return_error_response(request, 'page_not_found.html', 404)


def access_denied(request, *args, **kwargs):
    return return_error_response(request, 'access_denied.html', 401)


def server_error(request, *args, **kwargs):
    return return_error_response(request, 'server_error.html', 500)


def common_context_processor(request):
    if hasattr(settings, 'ENVIRONMENT'):
        env = settings.ENVIRONMENT
    else:
        env = 'DEV'
    context = {
        'environment': env,
        'installed_apps': settings.INSTALLED_APPS,
        'debug': settings.DEBUG,
        'logout_button': settings.LOGOUT_BUTTON,
        'email_service_desk': settings.EMAIL_SERVICE_DESK,
    }
    _check_notice(request, context)
    return context


def _check_notice(request, context):
    if 'subject' not in request.session and 'notice' not in request.session:
        notice = application_notice.find_current_notice()
        if notice:
            request.session.set_expiry(3600)
            request.session['subject'] = notice.subject
            request.session['notice'] = notice.notice
    if 'subject' in request.session and 'notice' in request.session:
        context['subject'] = request.session['subject']
        context['notice'] = request.session['notice']


def get_managed_programs(user) -> List[str]:
    managed_programs = []
    person = person_mdl.find_by_user(user)
    if person:
        managed_programs = api.get_managed_programs(person.global_id)
    return managed_programs


def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        authenticate(username=username, password=password)
    elif settings.OVERRIDED_LOGIN_URL:
        return redirect(settings.OVERRIDED_LOGIN_URL)
    return LoginView.as_view()(request)


def log_out(request):
    logout(request)
    if settings.OVERRIDED_LOGOUT_URL:
        return redirect(settings.OVERRIDED_LOGOUT_URL)
    return redirect('logged_out')


def logged_out(request):
    return layout.render(request, 'logged_out.html', {})
