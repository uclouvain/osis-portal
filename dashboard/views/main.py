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
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, permission_required
from .score_encoding import print_scores
from base import models as mdl_base
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponse
from base.views import layout


@login_required
def home(request):
    # Adapt layout depending on the type of user (student, professor)
    return layout.render(request, "dashboard.html")


@login_required
@permission_required('base.is_tutor', raise_exception=True)
def score_encoding(request):
    return layout.render(request, "score_encoding.html", {})


@login_required
@permission_required('base.is_tutor', raise_exception=True)
def download_papersheet(request):
    print("Inside dowload_papersheet()")
    person = mdl_base.person.find_by_user(request.user)
    pdf = print_scores(request, person.global_id)
    if pdf:
        filename = "%s.pdf" % _('scores_sheet')
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="%s"' % filename
        response.write(pdf)
        return response
    else:
        messages.add_message(request, messages.WARNING, _('no_score_to_encode'))
        return score_encoding(request)
