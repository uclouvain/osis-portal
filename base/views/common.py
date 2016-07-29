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

from django.contrib.auth.views import login as django_login
from django.contrib.auth import authenticate, logout
from django.shortcuts import render, redirect
from django.utils import translation
from base.views import layout
from base.models import person as person_mdl


def page_not_found(request):
    return layout.render(request, 'page_not_found.html', {})


def access_denied(request):
    return layout.render(request, 'access_denied.html', {})


def server_error(request):
    return layout.render(request, 'server_error.html', {})


def installed_applications_context_processor(request):
    return {'installed_apps': settings.INSTALLED_APPS}


def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        person = person_mdl.find_by_user(user)
        # ./manage.py createsuperuser (in local) doesn't create automatically a Person associated to User
        if person:
            if person.language:
                user_language = person.language
                translation.activate(user_language)
                request.session[translation.LANGUAGE_SESSION_KEY] = user_language
    elif settings.OVERRIDED_LOGIN_URL:
        return redirect(settings.OVERRIDED_LOGIN_URL)
    return django_login(request)


def log_out(request):
    if settings.OVERRIDED_LOGOUT_URL:
        return redirect(settings.OVERRIDED_LOGOUT_URL)
    logout(request)
    return redirect('logged_out')


def logged_out(request):
    return layout.render(request, 'logged_out.html', {})