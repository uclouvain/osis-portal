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
from compat import DjangoJSONEncoder
from django.conf import settings

from django.contrib.auth.views import LoginView
from django.contrib.auth import authenticate, logout
import json
from django.shortcuts import redirect
from django.utils import translation
from base.views import layout, api
from base.models import person as person_mdl
from osis_common.models import application_notice


def return_error_response(request, template, status_code):
    response = layout.render(request, template, {})
    response.status_code = status_code
    return response


def page_not_found(request, **kwargs):
    return return_error_response(request, 'page_not_found.html', 404)


def access_denied(request, **kwargs):
    return return_error_response(request, 'access_denied.html', 401)


def server_error(request, **kwargs):
    return return_error_response(request, 'server_error.html', 500)


def common_context_processor(request):
    if hasattr(settings, 'ENVIRONMENT'):
        env = settings.ENVIRONMENT
    else:
        env = 'DEV'
    context = {'environment': env,
               'installed_apps': settings.INSTALLED_APPS,
               'debug': settings.DEBUG,
               'logout_button': settings.LOGOUT_BUTTON}
    _check_notice(request, context)
    _set_managed_programs(request, context)
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


def _set_managed_programs(request, context):
    """
    1. Preconditions : user is authenticated and user is not a student.
    2. Check if the session key 'is_faculty_manager' is defined
        2.1. If yes, Context 'is_faculty_manager' is updated with value of Session 'is_faculty_manager'
        2.2. If not :
            2.2.1: The managed programs are retrieved from osis with call to the api
            2.2.2: If the managed programs exists :
                2.2.2.1: Context 'is_faculty_manager' value is set to True
                2.2.2.2: Session 'is_faculty_manager'  value is set to True
                2.2.2.3: Session 'managed_programs' value is set with the results of the api call
            2.2.3: If not:
                2.2.3.1: Context 'is_faculty_manager' value is set to False
                2.2.3.2: Session 'is_faculty_manager'  value is set to False
                2.2.3.3: Session 'managed_programs' value is set to None
    """
    if request.user.is_authenticated:
        if request.user.is_superuser or not request.user.has_perm('base.is_student'):
            if request.session.get('is_faculty_manager') is None:
                if request.user.has_perm('base.is_faculty_administrator'):
                    context['is_faculty_manager'] = True
                    request.session['is_faculty_manager'] = True
                else:
                    is_faculty_manager = False
                    managed_programs = None
                    managed_programs_as_dict = get_managed_program_as_dict(request.user)
                    if managed_programs_as_dict:
                        is_faculty_manager = True
                        managed_programs = json.dumps(managed_programs_as_dict, cls=DjangoJSONEncoder)
                    context['is_faculty_manager'] = is_faculty_manager
                    request.session['is_faculty_manager'] = is_faculty_manager
                    request.session['managed_programs'] = managed_programs
            else:
                context['is_faculty_manager'] = request.session.get('is_faculty_manager')
        elif not request.user.is_superuser:
            request.session['is_faculty_manager'] = False
            request.session['managed_programs'] = None
            context['is_faculty_manager'] = False


def get_managed_program_as_dict(user):
    managed_programs_as_dict = None
    person = person_mdl.find_by_user(user)
    if person:
        managed_programs_as_dict = api.get_managed_programs_as_dict(person.global_id)
    return managed_programs_as_dict


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
    return LoginView.as_view()(request)


def log_out(request):
    logout(request)
    if settings.OVERRIDED_LOGOUT_URL:
        return redirect(settings.OVERRIDED_LOGOUT_URL)
    return redirect('logged_out')


def logged_out(request):
    return layout.render(request, 'logged_out.html', {})
