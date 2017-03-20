##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2017 Université catholique de Louvain (http://www.uclouvain.be)
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
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.urlresolvers import reverse

from django.http import HttpResponseRedirect
from django.utils import translation
from django.utils.translation import ugettext as _

from base import models as mdl


from base.views import layout


@login_required
def my_osis_index(request):
    return layout.render(request, "my_osis/profile.html", {})


@login_required
def profile(request):
    person = mdl.person.find_by_user(request.user)
    return layout.render(request, "my_osis/profile.html", {'person':                person,
                                                           'supported_languages':   settings.LANGUAGES,
                                                           'default_language':      settings.LANGUAGE_CODE})

@login_required
def profile_lang(request):
    ui_language = request.POST.get('ui_language')
    mdl.person.change_language(request.user, ui_language)
    translation.activate(ui_language)
    request.session[translation.LANGUAGE_SESSION_KEY] = ui_language
    return profile(request)